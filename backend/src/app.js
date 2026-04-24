const express = require("express");
const cors = require("cors");
require("dotenv").config();
const errorHandler = require("./core/middleware/error.middleware");
const { processJob } = require("./core/workers/worker");
const { errorMiddleware } = require("./middleware/error.middleware");

const app = express();
app.use(cors());
app.use(express.json());

app.get("/health", (req, res) => {
    res.json({
        status: "ok",
        service: "backend",
    });
});
const apiRoutes = require("./modules");
const uploadRoutes = require("./modules/upload/upload.routes");
const jobRoutes = require("./modules/job/job.routes");

app.use("/api", apiRoutes);
app.use("/api/upload", uploadRoutes);
app.use("/api/job", jobRoutes);
app.post("/api/test/process/:jobId", async (req, res) => {
    try {
        const job = await processJob(req.params.jobId);
        res.json({ success: true, job });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

app.use(errorHandler);
app.use(errorMiddleware);

module.exports = app;