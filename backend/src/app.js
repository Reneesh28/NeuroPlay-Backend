const express = require("express");
const cors = require("cors");
require("dotenv").config();

const errorHandler = require("./core/middleware/error.middleware");
// ❌ REMOVE duplicate middleware import
// const { errorMiddleware } = require("./middleware/error.middleware");

const { processJob } = require("./core/workers/worker");

const app = express();

app.use(cors());
app.use(express.json());

// 🔥 Health Check
app.get("/health", (req, res) => {
    res.json({
        status: "ok",
        service: "backend",
    });
});

// 🔥 Routes
const apiRoutes = require("./modules");
const uploadRoutes = require("./modules/upload/upload.routes");
const jobRoutes = require("./modules/job/job.routes");

app.use("/api", apiRoutes);
app.use("/api/upload", uploadRoutes);
app.use("/api/job", jobRoutes);

// 🔥 Manual test endpoint
app.post("/api/test/process/:jobId", async (req, res) => {
    try {
        const job = await processJob(req.params.jobId);
        res.json({ success: true, job });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// 🔥 SINGLE error handler (important)
app.use(errorHandler);

module.exports = app;