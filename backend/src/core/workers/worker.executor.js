const Job = require("../jobs/job.model");
const stepRegistry = require("../pipeline/step.registry");
const { assertValidStep } = require("../pipeline/step.validator");
const { updateStepStatus } = require("../jobs/job.service");
const { validateWorkerPayload } = require("./worker.validator");
const producer = require("../queue/producer");
const { classifyError, ErrorTypes } = require("../resilience/error.classifier");
const { shouldRetry } = require("../resilience/retry.manager");
const { TIMEOUT_CONFIG } = require("../resilience/timeout.manager");



/**
 * 🔥 SINGLE STEP EXECUTION ENGINE (Refactored)
 * Worker = Execution + Forwarding only. No decision making.
 */
const executeJobStep = async (payload) => {
    // 1. Validate Payload
    validateWorkerPayload(payload);

    const { job_id, step, input_ref, context } = payload;
    const trace_id = context?.trace_id || "no-trace";

    console.log(`[JOB:START] [${step}] [ID:${job_id}] [TRACE:${trace_id}] 🚀 Starting step execution`);

    // 2. Trust Payload Input
    const inputData = input_ref;

    const processor = stepRegistry[step];
    if (!processor) {
        console.error(`[JOB:ERROR] [${step}] [ID:${job_id}] [TRACE:${trace_id}] ❌ Processor not found`);
        throw new Error(`Processor not found for step: ${step}`);
    }

    // 3. Fetch Job for Update Context
    const job = await Job.findOne({ job_id });
    if (!job) {
        console.error(`[JOB:ERROR] [${step}] [ID:${job_id}] [TRACE:${trace_id}] ❌ Job not found in DB`);
        throw new Error(`Job not found: ${job_id}`);
    }

    if (job.current_step !== step) {
        console.warn(`[JOB:WARN] [${step}] [ID:${job_id}] [TRACE:${trace_id}] ⚠️ Step mismatch: expected ${job.current_step}`);
        throw new Error(`Step mismatch: expected ${job.current_step}, got ${step}`);
    }

    try {
        console.log(`[JOB:INFO] [${step}] [ID:${job_id}] [TRACE:${trace_id}] ➡️ Calling processor...`);

        // 4. EXECUTION
        const result = await processor(job, inputData);

        // 5. Response Validation
        if (!result || typeof result !== "object") {
            throw new Error("Invalid processor response contract");
        }

        if (result.status === "failed") {
            throw new Error(result.error?.message || "Processor execution reported failure");
        }

        // 6. UPDATE & FORWARD
        const output_ref = result?.output ?? null;
        const next_step = result?.next_step ?? null;
        const execution_mode = result?.execution_mode ?? "FULL";

        if (next_step) assertValidStep(next_step);

        const updatedJob = await updateStepStatus(job._id, step, {
            status: "completed",
            output_ref: output_ref,
            next_step: next_step,
            execution_mode: execution_mode,
            resolved_model_version: result?.model_version ?? null
        });

        console.log(`[JOB:STEP_OK] [${step}] [ID:${job_id}] [TRACE:${trace_id}] ✅ Step completed. Mode: ${execution_mode}`);

        // 7. NEXT STEP ENQUEUING
        if (next_step) {
            await producer.enqueueJobStep(updatedJob, next_step, output_ref);
            console.log(`[JOB:FORWARD] [${step}] [ID:${job_id}] [TRACE:${trace_id}] ➡️ Forwarding to ${next_step}`);
        } else {
            console.log(`[JOB:FINISH] [${step}] [ID:${job_id}] [TRACE:${trace_id}] 🏁 Job lifecycle finished`);
        }

    } catch (error) {
        // 🔥 Use Centralized Resilience Layer
        const errorType = classifyError(error);
        const retryCount = payload.attemptsMade || 0; // BullMQ provides this

        console.error(`[JOB:FAIL] [${step}] [ID:${job_id}] [TRACE:${trace_id}] ❌ Error [${errorType}]: ${error.message}`);

        // 1. Handle ML_FAILURE → Continue if possible (Strategy: FALLBACK)
        if (errorType === ErrorTypes.ML_FAILURE && error.next_step) {
            console.warn(`[JOB:FALLBACK] [${step}] [ID:${job_id}] [TRACE:${trace_id}] ⚠️ ML Failure, continuing to ${error.next_step}`);
            
            const updatedJob = await updateStepStatus(job._id, step, {
                status: "completed",
                execution_mode: "FALLBACK",
                error: { message: error.message, type: ErrorTypes.ML_FAILURE },
                next_step: error.next_step
            });

            await producer.enqueueJobStep(updatedJob, error.next_step, inputData);
            return;
        }

        // 2. Fail the step in DB
        await updateStepStatus(job._id, step, {
            status: "failed",
            error: {
                message: error.message,
                type: errorType
            }
        });

        // 3. Decide on Retry vs DLQ
        if (shouldRetry(errorType, retryCount)) {
            console.log(`[JOB:RETRY] [${step}] [ID:${job_id}] [TRACE:${trace_id}] 🔄 Attempt ${retryCount + 1} - Retrying...`);
            throw error; // Let BullMQ handle the backoff
        }

        // 4. Move to DLQ on Permanent/Exhausted Failure
        console.error(`[JOB:DEAD] [${step}] [ID:${job_id}] [TRACE:${trace_id}] 💀 Giving up. Moving to DLQ.`);
        await producer.moveToDLQ(job, step, error.message);
    }


};

module.exports = {
    executeJobStep
};