const { Worker } = require("bullmq");
const connection = require("../../config/redis");

const { processJob } = require("../workers/worker");

const jobWorker = new Worker(
    "jobQueue",
    async (job) => {
        const { jobId } = job.data;

        console.log("🚀 Processing Job:", jobId);

        await processJob(jobId);
    },
    {
        connection,
    }
);

jobWorker.on("completed", (job) => {
    console.log(`✅ Job ${job.id} completed`);
});

jobWorker.on("failed", (job, err) => {
    console.error(`❌ Job ${job.id} failed:`, err.message);
});

module.exports = jobWorker;