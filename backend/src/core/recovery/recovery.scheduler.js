const Job = require("../jobs/job.model");
const { handleDeadJob } = require("../resilience/dlq.handler");

const STUCK_THRESHOLD = 5 * 60 * 1000; // 5 minutes
const INTERVAL = 10 * 1000; // run every 10 seconds

async function detectStuckJobs() {
    const now = Date.now();

    const stuckJobs = await Job.find({
        status: "processing",
        last_heartbeat: { $lt: new Date(now - STUCK_THRESHOLD) }
    });

    for (const job of stuckJobs) {
        console.error(`🚨 [STUCK] Job ${job.job_id} is stuck`);

        await handleDeadJob(
            job,
            job.current_step,
            new Error("JOB_STUCK_TIMEOUT")
        );
    }
}

// 🔥 THIS WAS MISSING
function startRecoveryScheduler() {
    console.log("🛠️ Recovery Scheduler Started...");

    setInterval(async () => {
        try {
            await detectStuckJobs();
        } catch (err) {
            console.error("❌ Recovery Scheduler Error:", err);
        }
    }, INTERVAL);
}

module.exports = {
    detectStuckJobs,
    startRecoveryScheduler // ✅ now exported
};