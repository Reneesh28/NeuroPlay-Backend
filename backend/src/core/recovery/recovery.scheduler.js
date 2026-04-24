const Job = require("../jobs/job.model");
const { handleDeadJob } = require("../resilience/dlq.handler");

const STUCK_THRESHOLD = 5 * 60 * 1000; // 5 minutes

async function detectStuckJobs() {
    const now = new Date();

    const stuckJobs = await Job.find({
        status: "processing",
        last_heartbeat: { $lt: new Date(now - STUCK_THRESHOLD) }
    });

    for (const job of stuckJobs) {
        console.error(`[STUCK] Job ${job.job_id} is stuck`);

        await handleDeadJob(job, job.current_step, new Error("JOB_STUCK_TIMEOUT"));
    }
}

module.exports = {
    detectStuckJobs
};