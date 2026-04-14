const express = require("express");
const router = express.Router();

const jobService = require("../core/jobs/job.service");

// Get job by ID
router.get("/:id", async (req, res, next) => {
    try {
        const job = await jobService.getJob(req.params.id);

        if (!job) {
            return res.status(404).json({
                success: false,
                message: "Job not found",
            });
        }

        res.json({
            success: true,
            data: job,
        });
    } catch (error) {
        next(error);
    }
});

module.exports = router;