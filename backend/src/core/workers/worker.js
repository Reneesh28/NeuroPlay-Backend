const { Worker } = require("bullmq");
const connection = require("../../config/redis"); // your redis config
const { executeJobStep } = require("./worker.executor");

const worker = new Worker(
    "processJob",
    async (job) => {
        try {
            console.log(`📥 Worker received: ${job.data.step} for Job: ${job.data.job_id}`);

            await executeJobStep(job.data);

        } catch (err) {

            console.error("❌ Worker error:", err.message);
            throw err;
        }
    },
    { connection }
);

module.exports = worker;