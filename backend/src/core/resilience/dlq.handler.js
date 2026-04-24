const producer = require("../queue/producer");

/**
 * 🔥 DLQ HANDLER
 * Manages the transition of failed jobs to the Dead Letter Queue.
 * Ensures metadata is enriched before burial.
 */
async function handleDeadJob(job, step, error) {
    if (!job || !step) {
        throw new Error("Job and Step are required for DLQ handling");
    }

    const deadPayload = {
        job_id: job.job_id,
        step: step,
        error: typeof error === "string" ? error : error.message,
        failed_at: new Date().toISOString(),
        trace_id: job.context?.trace_id,
        
        // Enrich with last known state
        last_execution_mode: job.execution_mode,
        completed_steps: job.completed_steps_count,
        total_steps: job.total_steps_count
    };

    console.error(`[DLQ:BURIAL] 💀 Job ${job.job_id} is dead. Burying in DLQ...`);

    // Call producer to move it to the actual queue
    return await producer.moveToDLQ(job, step, deadPayload);
}

module.exports = {
    handleDeadJob
};
