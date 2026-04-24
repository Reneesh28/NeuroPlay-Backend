const { Worker } = require("bullmq");
const connection = require("../../config/redis");
const { executeJobStep } = require("./worker.executor");

/**
 * 🔥 NEUROPLAY WORKER CLUSTER
 * Starts workers for all step-based queues to ensure distributed execution.
 */

const QUEUE_NAMES = [
    "ingestion-queue",
    "processing-queue",
    "embedding-queue",
    "simulation-queue"
];

console.log("👷 Starting NeuroPlay Worker Cluster...");

QUEUE_NAMES.forEach(queueName => {
    new Worker(
        queueName,
        async (job) => {
            try {
                // All worker logic is delegated to the executor
                await executeJobStep(job.data);
            } catch (err) {
                // Error handled in executor, but we log here as a final safety net
                console.error(`❌ Fatal Worker Error in [${queueName}]:`, err.message);
                throw err; // Allow BullMQ to handle retry/fail
            }
        },
        { 
            connection,
            concurrency: 5 // Allow 5 concurrent jobs per worker instance
        }
    );
    console.log(`✅ Worker listening on [${queueName}]`);
});

// We don't export anything as this is an entry-point script