const express = require("express");
const router = express.Router();

const { getJob, getUserJobs, listDLQ, replayJob, cancelJob } = require("./job.controller");
const { authMiddleware } = require("../../middleware/auth.middleware");

// 🔥 GET ALL USER JOBS
router.get("/", authMiddleware, getUserJobs);

// 🔥 GET JOB STATUS + RESULT
router.get("/:id", getJob);

// 🔥 DLQ MANAGEMENT
router.get("/dlq/list", authMiddleware, listDLQ);
router.post("/dlq/:jobId/replay", authMiddleware, replayJob);

// 🔥 JOB ACTIONS
router.post("/:id/cancel", authMiddleware, cancelJob);

module.exports = router;