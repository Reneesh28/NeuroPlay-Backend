const Job = require("../jobs/job.model");
const stepRegistry = require("../pipeline/step.registry");
const { assertValidStep, assertStepOrder } = require("../pipeline/step.validator");
const { updateStepStatus } = require("../jobs/job.service");
const { validateWorkerPayload } = require("./worker.validator");
const producer = require("../queue/producer");

const { classifyError } = require("../resilience/error.classifier");
const { handleDeadJob } = require("../resilience/dlq.handler");
const { shouldRetry } = require("../resilience/retry.manager");
const { TIMEOUT_CONFIG } = require("../resilience/timeout.manager");

const { VALID_EXECUTION_MODES, EXECUTION_MODES } = require("../constants/execution.constants");
const { resolveNextExecutionMode } = require("../execution.guard");

// ==============================
// 🚀 MAIN EXECUTOR
// ==============================
const executeJobStep = async (payload) => {
    validateWorkerPayload(payload);

    const { job_id, step, input_ref, context } = payload;

    console.log(`[JOB:START] [${step}] [${job_id}]`);

    const processor = stepRegistry[step];
    if (!processor) throw new Error(`Processor not found for step: ${step}`);

    const job = await Job.findOne({ job_id });
    if (!job) throw new Error(`Job not found`);

    // 🔥 Fix step mismatch instead of crash
    if (job.current_step !== step) {
        console.warn(
            `⚠️ Step mismatch detected → fixing: ${job.current_step} → ${step}`
        );

        job.current_step = step;
        await job.save();
    }

    let execution_mode = job.execution_mode || EXECUTION_MODES.FULL;

    try {
        const result = await Promise.race([
            processor(job, input_ref),
            new Promise((_, reject) =>
                setTimeout(() => reject(new Error("STEP_TIMEOUT")), TIMEOUT_CONFIG.STEP_TIMEOUT)
            )
        ]);

        // ==============================
        // 🔒 VALIDATION
        // ==============================
        if (!result || typeof result !== "object") {
            throw new Error("Invalid response from processor");
        }

        if (!VALID_EXECUTION_MODES.includes(result.execution_mode)) {
            throw new Error(`Invalid execution_mode: ${result.execution_mode}`);
        }

        if (!("output" in result)) {
            throw new Error("Missing output in processor response");
        }

        // 🔥 SAFE OUTPUT (STRING ONLY)
        const output_ref =
            typeof result.output === "string"
                ? result.output
                : null;

        const next_step = result.next_step || null;

        // 🔥 MODE PROPAGATION
        execution_mode = resolveNextExecutionMode(
            execution_mode,
            result.execution_mode
        );

        // 🔒 STEP VALIDATION
        if (next_step) {
            assertValidStep(next_step);
            assertStepOrder(step, next_step);
        }

        // ==============================
        // 💾 UPDATE STATE
        // ==============================
        const updatedJob = await updateStepStatus(job._id, step, {
            status: "completed",
            output_ref,
            next_step,
            execution_mode
        });

        // ==============================
        // 🔁 PIPELINE CONTINUE
        // ==============================
        if (next_step) {
            await producer.enqueueJobStep(
                {
                    job_id: updatedJob.job_id,
                    context: updatedJob.context
                },
                next_step,
                output_ref // 🔥 correct chaining
            );
        } else {
            console.log(`✅ PIPELINE COMPLETE | Job:${job_id}`);
        }

    } catch (error) {
        const errorType = classifyError(error);

        console.error(`[JOB:ERROR] [${step}] [${job_id}]`, {
            message: error.message,
            type: errorType
        });

        await updateStepStatus(job._id, step, {
            status: "failed",
            execution_mode,
            error: { message: error.message, type: errorType }
        });

        if (shouldRetry(errorType)) {
            throw error;
        }

        await handleDeadJob(job, step, error);
    }
};

module.exports = {
    executeJobStep
};