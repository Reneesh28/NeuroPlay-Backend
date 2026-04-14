const express = require("express");
const router = express.Router();

const jobService = require("../core/jobs/job.service");
const producer = require("../core/queue/producer");
const pipeline = require("../core/pipeline/pipeline.config");

// Create test job (WITH INPUT)
router.post("/test-job", async (req, res, next) => {
    try {
        const { input } = req.body; // 🔥 NEW

        // Step 1: Create job in DB
        const job = await jobService.createJob({
            user_id: "test-user",
            session_id: "test-session",
            steps: pipeline.map((step) => ({
                name: step,
            })),
        });

        // Step 2: Push to queue WITH input
        await producer.addJob("test-job", {
            jobId: job._id,
            inputData: input || {},
        });

        res.json({
            success: true,
            job_id: job._id,
        });
    } catch (error) {
        next(error);
    }
});

module.exports = router;