const { deadLetterQueue } = require("./queues");
const { getQueueForStep } = require("./queue.router");
const { buildQueuePayload } = require("./queue.contracts");

class QueueProducer {
    /**
     * Enqueue a job step with the strict v1 contract and correct routing
     */
    async enqueueJobStep(job, step, input_ref = null) {
        if (!job || !step) {
            throw new Error("Job and Step are required to enqueue");
        }

        const queue = getQueueForStep(step);
        const payload = buildQueuePayload({ job, step, input_ref });


        console.log(`📡 Enqueuing: ${step} on [${queue.name}] for Job: ${job.job_id}`);

        return await queue.add("processJob", payload, {
            attempts: 3,
            backoff: {
                type: "exponential",
                delay: 1000
            },
            timeout: 60000, // 1 minute step timeout
            removeOnComplete: true,
            removeOnFail: false // Keep in failed state for visibility
        });

    }

    /**
     * Move a job to the Dead Letter Queue for manual intervention
     */
    async moveToDLQ(job, step, error) {
        const payload = buildQueuePayload({ job, step });
        payload.error = error;
        payload.failed_at = new Date().toISOString();

        console.error(`💀 Moving Job: ${job.job_id} to DLQ. Error: ${error}`);

        return await deadLetterQueue.add("failedJob", payload);
    }
}

module.exports = new QueueProducer();
