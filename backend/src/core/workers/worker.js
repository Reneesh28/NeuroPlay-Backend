const { Worker } = require("bullmq");
const queueConfig = require("../queue/queue.config");
const defaultProcessor = require("./processors/default.processor");

const connectDB = require("../../config/db");
require("../../config/redis");

// 🔥 IMPORTANT: connect DB for worker
connectDB();

const worker = new Worker(
    "default-queue",
    async (job) => {
        return defaultProcessor(job);
    },
    queueConfig
);

worker.on("completed", (job) => {
    console.log(`🎉 Job ${job.id} completed`);
});

worker.on("failed", (job, err) => {
    console.error(`❌ Job ${job.id} failed:`, err);
});

console.log("🚀 Worker started");