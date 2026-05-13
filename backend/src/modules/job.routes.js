const express = require("express");
const router = express.Router();

const jobService = require("../core/jobs/job.service");
const { successResponse, errorResponse } = require("../contracts/api.contract");

// Get job by ID
router.get("/:id", async (req, res, next) => {
    try {
        const job = await jobService.getJob(req.params.id);

        if (!job) {
            return res.status(404).json(
                errorResponse({ 
                    message: "Job not found",
                    code: "JOB_NOT_FOUND" 
                }, {
                    trace_id: req.headers['x-trace-id']
                })
            );
        }

        return res.json(
            successResponse(job, {
                trace_id: req.headers['x-trace-id']
            })
        );
    } catch (error) {
        next(error);
    }
});

module.exports = router;