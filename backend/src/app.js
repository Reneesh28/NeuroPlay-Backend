const express = require("express");
const cors = require("cors");
require("dotenv").config();

const errorHandler = require("./core/middleware/error.middleware");
// ❌ REMOVE duplicate middleware import
// const { errorMiddleware } = require("./middleware/error.middleware");

const { processJob } = require("./core/workers/worker");

const { traceMiddleware } = require("./middleware/trace.middleware");
const { apiLimiter } = require("./middleware/limiter.middleware");

const app = express();

app.use(cors());
app.use(express.json());
app.use(traceMiddleware);

// 🔥 Global limiter removed to avoid ERR_ERL_DOUBLE_COUNT.
// Limits are now handled per-module in their routes (e.g. simulation, upload).

const mongoose = require("mongoose");
const redisClient = require("./config/redis");

// 🔥 Health Check
app.get("/health", async (req, res) => {
    const mongoStatus = mongoose.connection.readyState === 1 ? "ok" : "error";
    let redisStatus = "error";
    try {
        await redisClient.ping();
        redisStatus = "ok";
    } catch (e) {}

    const status = (mongoStatus === "ok" && redisStatus === "ok") ? "ok" : "degraded";

    res.status(status === "ok" ? 200 : 503).json({
        status,
        service: "backend",
        dependencies: {
            mongodb: mongoStatus,
            redis: redisStatus
        },
        uptime: process.uptime()
    });
});

// 🔥 Routes
const apiRoutes = require("./modules");

app.use("/api", apiRoutes);

const { successResponse, errorResponse } = require("./contracts/api.contract");

// 🔥 Manual test endpoint
app.post("/api/test/process/:jobId", async (req, res) => {
    try {
        const job = await processJob(req.params.jobId);
        return res.json(
            successResponse(job, {
                trace_id: req.headers['x-trace-id']
            })
        );
    } catch (err) {
        return res.status(500).json(
            errorResponse(err, {
                trace_id: req.headers['x-trace-id']
            })
        );
    }
});

// 🔥 SINGLE error handler (important)
app.use(errorHandler);

module.exports = app;