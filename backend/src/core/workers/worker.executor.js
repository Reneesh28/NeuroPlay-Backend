const Job = require("../jobs/job.model");
const stepRegistry = require("../pipeline/step.registry");
const { assertValidStep } = require("../pipeline/step.validator");
const { updateStepStatus } = require("../jobs/job.service");
const { validateWorkerPayload } = require("./worker.validator");
const producer = require("../queue/producer");

const { classifyError, ErrorTypes } = require("../resilience/error.classifier");
const { handleDeadJob } = require("../resilience/dlq.handler");
const { shouldRetry } = require("../resilience/retry.manager");
const { TIMEOUT_CONFIG } = require("../resilience/timeout.manager");

const { VALID_EXECUTION_MODES, EXECUTION_MODES } = require("../constants/execution.constants");

/**
 * 🔥 FINAL WORKER EXECUTION ENGINE (STEP 4.3 READY)
 */
const executeJobStep = async (payload) => {
    validateWorkerPayload(payload);

    const { job_id, step, input_ref, context } = payload;
    const trace_id = context?.trace_id || "no-trace";

    console.log(`[JOB:START] [${step}] [ID:${job_id}] [TRACE:${trace_id}] 🚀`);

    if (!input_ref) {
        throw new Error(`Missing input_ref for step: ${step}`);
    }

    const inputData = input_ref;

    const processor = stepRegistry[step];
    if (!processor) throw new Error(`Processor not found for step: ${step}`);

    const job = await Job.findOne({ job_id });
    if (!job) throw new Error(`Job not found: ${job_id}`);

    if (job.current_step !== step) {
        throw new Error(`Step mismatch: expected ${job.current_step}, got ${step}`);
    }

    // 🔥 STEP 4.3 — SET JOB START TIME (ONLY ONCE)
    if (!job.started_at) {
        job.started_at = new Date();
        job.last_heartbeat = new Date(); // initialize heartbeat
        await job.save();

        console.log(`[JOB:INIT] Job ${job_id} started at ${job.started_at.toISOString()}`);
    }

    let execution_mode = EXECUTION_MODES.FULL;

    try {
        console.log(`[JOB:EXEC] [${step}]`);

        // 🔥 TIMEOUT WRAP
        const result = await Promise.race([
            processor(job, inputData),
            new Promise((_, reject) =>
                setTimeout(() => reject(new Error("STEP_TIMEOUT")), TIMEOUT_CONFIG.STEP_TIMEOUT)
            )
        ]);

        // 🔥 STRICT RESPONSE VALIDATION
        if (!result || typeof result !== "object") {
            throw new Error("Invalid processor response contract");
        }

        if (result.status !== "completed") {
            throw new Error(result.error?.message || "Processor failed");
        }

        if (!("output" in result)) {
            throw new Error("Missing output in processor response");
        }

        if (!("execution_mode" in result)) {
            throw new Error("Missing execution_mode from AI response");
        }

        if (!VALID_EXECUTION_MODES.includes(result.execution_mode)) {
            throw new Error(`Invalid execution_mode: ${result.execution_mode}`);
        }

        execution_mode = result.execution_mode;

        const output_ref = result.output;
        const next_step = result.next_step || null;

        if (next_step) assertValidStep(next_step);

        // 🔥 PARTIAL MODE LOGGING
        if (execution_mode === EXECUTION_MODES.PARTIAL) {
            console.warn(`[JOB:PARTIAL] ${step} executed with degraded quality`);
        }

        // 🔥 UPDATE JOB
        const updatedJob = await updateStepStatus(job._id, step, {
            status: "completed",
            output_ref,
            next_step,
            execution_mode,
            resolved_model_version: result.model_version ?? null
        });

        console.log(`[JOB:OK] [${step}] [MODE:${execution_mode}]`);

        // 🔥 FORWARD
        if (next_step) {
            await producer.enqueueJobStep(updatedJob, next_step, output_ref);
            console.log(`[JOB:NEXT] ${step} → ${next_step}`);
        } else {
            console.log(`[JOB:DONE] ${job_id}`);
        }

    } catch (error) {
        const errorType = classifyError(error);

        const retryCount =
            job?.steps?.find(s => s.name === step)?.retries || 0;

        console.error(`[JOB:FAIL] [${step}] [${errorType}] ${error.message}`);

        // 🔥 FALLBACK MODE
        if (execution_mode === EXECUTION_MODES.FALLBACK && error.next_step) {
            const updatedJob = await updateStepStatus(job._id, step, {
                status: "completed",
                execution_mode: EXECUTION_MODES.FALLBACK,
                error: { message: error.message, type: errorType },
                next_step: error.next_step
            });

            await producer.enqueueJobStep(updatedJob, error.next_step, inputData);
            return;
        }

        // 🔥 ML FAILURE
        if (errorType === ErrorTypes.ML_FAILURE && error.next_step) {
            const updatedJob = await updateStepStatus(job._id, step, {
                status: "completed",
                execution_mode: EXECUTION_MODES.FALLBACK,
                error: { message: error.message, type: ErrorTypes.ML_FAILURE },
                next_step: error.next_step
            });

            await producer.enqueueJobStep(updatedJob, error.next_step, inputData);
            return;
        }

        // 🔴 FAIL STEP
        await updateStepStatus(job._id, step, {
            status: "failed",
            execution_mode,
            error: { message: error.message, type: errorType }
        });

        // 🔁 RETRY DECISION
        if (shouldRetry(errorType, retryCount, execution_mode)) {
            console.log(`[JOB:RETRY] attempt ${retryCount + 1}`);
            throw error;
        }

        // 💀 DLQ
        await handleDeadJob(job, step, error);
    }
};

module.exports = {
    executeJobStep
};