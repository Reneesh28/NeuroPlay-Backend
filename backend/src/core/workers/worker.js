const { Worker } = require("bullmq");
const connection = require("../../config/redis");
const { executeJobStep } = require("./worker.executor");

const QUEUE_NAMES = [
    "ingestion-queue",
    "processing-queue",
    "embedding-queue", // 🔥 covers embedding + memory
    "simulation-queue"
];

const CONCURRENCY = 5;

console.log("👷 Starting NeuroPlay Worker Cluster...");

const workers = QUEUE_NAMES.map(queueName => {
    const worker = new Worker(
        queueName,
        async (job) => {
            try {
                await executeJobStep(job.data);
            } catch (err) {
                console.error(`❌ Worker Error [${queueName}] Job ${job?.id}:`, err.message);
                throw err;
            }
        },
        {
            connection,
            concurrency: CONCURRENCY,
        }
    );

    worker.on("completed", (job) => {
        console.log(`[WORKER:${queueName}] ✅ Job ${job.id} completed`);
    });

    worker.on("failed", (job, err) => {
        console.error(`[WORKER:${queueName}] ❌ Job ${job?.id} failed: ${err.message}`);
    });

    console.log(`✅ Worker listening on [${queueName}]`);

    return worker;
});

// Graceful shutdown
async function shutdown() {
    console.log("🛑 Shutting down workers...");
    await Promise.all(workers.map(w => w.close()));
    process.exit(0);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);