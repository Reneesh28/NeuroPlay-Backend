const Job = require("../jobs/job.model");
const { handleDeadJob } = require("../resilience/dlq.handler");
const connection = require("../../config/redis");
const { TIMEOUT_CONFIG } = require("../resilience/timeout.manager");

// 🔥 Dynamic threshold (2x step timeout)
const STUCK_THRESHOLD = TIMEOUT_CONFIG.STEP_TIMEOUT * 2;

async function detectStuckJobs() {
    const lockKey = "stuck_job_detector_lock";

    // 🔥 Distributed lock
    const lock = await connection.set(lockKey, "locked", {
        NX: true,
        EX: 50
    });

    if (!lock) {
        console.log("[LOCK] Detector already running on another instance");
        return;
    }

    try {
        const now = new Date();

        const stuckJobs = await Job.find({
            status: "processing",
            last_heartbeat: { $lt: new Date(now - STUCK_THRESHOLD) }
        });

        for (const job of stuckJobs) {
            console.error(`[STUCK] Job ${job.job_id} stuck at step ${job.current_step}`);

            await handleDeadJob(
                job,
                job.current_step,
                new Error("JOB_STUCK_TIMEOUT")
            );
        }

    } catch (err) {
        console.error("[STUCK DETECTOR ERROR]", err);
    }
}

module.exports = {
    detectStuckJobs
};