const producer = require("../queue/producer");

/**
 * 🔥 DLQ HANDLER (FIXED)
 */
async function handleDeadJob(job, step, error) {
    if (!job || !step) {
        throw new Error("Job and Step are required for DLQ handling");
    }

    const stepData = job.steps.find(s => s.name === step);

    const deadPayload = {
        job_id: job.job_id,
        step,
        error: typeof error === "string" ? error : error.message,
        failed_at: new Date().toISOString(),
        trace_id: job.context?.trace_id,

        // 🔥 FIXED (step-level, not job-level)
        last_execution_mode: stepData?.execution_mode || "UNKNOWN",

        completed_steps: job.steps.filter(s => s.status === "completed").length,
        total_steps: job.steps.length
    };

    console.error(`[DLQ:BURIAL] 💀 Job ${job.job_id} is dead`);

    return await producer.moveToDLQ(job, step, deadPayload);
}

module.exports = {
    handleDeadJob
};