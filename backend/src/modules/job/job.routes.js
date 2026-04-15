const express = require("express");
const router = express.Router();

const { getJob } = require("./job.controller");

// 🔥 GET JOB STATUS + RESULT
router.get("/:id", getJob);

module.exports = router;