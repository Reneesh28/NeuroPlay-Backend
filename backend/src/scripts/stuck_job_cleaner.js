const Job = require("../core/jobs/job.model");
const producer = require("../core/queue/producer");

/**
 * 🔥 Stuck Job Cleaner
 * Finds jobs stuck in 'processing' state and fails them
 */
async function cleanStuckJobs() {
    const STUCK_THRESHOLD = 5 * 60 * 1000; // 5 minutes
    const now = new Date();

    console.log(`🧹 Running Stuck Job Cleaner at ${now.toISOString()}`);

    try {
        const stuckJobs = await Job.find({
            status: "processing",
            updatedAt: { $lt: new Date(Date.now() - STUCK_THRESHOLD) }
        });

        if (stuckJobs.length === 0) {
            console.log("✅ No stuck jobs found.");
            return;
        }

        console.log(`⚠️ Found ${stuckJobs.length} stuck jobs. failing them...`);

        for (const job of stuckJobs) {
            console.log(`💀 Failing stuck Job: ${job.job_id}`);
            
            job.status = "failed";
            const currentStep = job.steps.find(s => s.name === job.current_step);
            if (currentStep) {
                currentStep.status = "failed";
                currentStep.error = { message: "Job timed out (Stuck in processing)" };
            }

            await job.save();

            // Move to DLQ
            await producer.moveToDLQ(job, job.current_step || "unknown", "TIMEOUT");
        }

        console.log("✅ Cleanup finished.");

    } catch (error) {
        console.error("❌ Stuck Job Cleaner error:", error.message);
    }
}

// Export for manual run or cron
module.exports = cleanStuckJobs;
