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
        const { buildContext } = require("../core/jobs/context.builder");
        const context = buildContext({
            user_id: "test-user",
            session_id: "test-session",
            game_id: "test-game",
            domain: "test-domain"
        });

        const job = await jobService.createJob({
            context,
            input_ref: input || { url: "test-url" }
        });

        // Step 2: Push to queue WITH input
        await producer.enqueueJobStep(job, job.current_step);


        res.json({
            success: true,
            job_id: job._id,
        });
    } catch (error) {
        next(error);
    }
});

module.exports = router;