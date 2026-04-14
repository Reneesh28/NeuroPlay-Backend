const express = require("express");
const cors = require("cors");

const errorHandler = require("./core/middleware/error.middleware");

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Health check
app.get("/health", (req, res) => {
    res.json({
        status: "ok",
        service: "backend",
    });
});

// Routes
const apiRoutes = require("./modules");
app.use("/api", apiRoutes);

// Error middleware (ALWAYS LAST)
app.use(errorHandler);

module.exports = app;