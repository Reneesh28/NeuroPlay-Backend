const express = require("express");
const router = express.Router();

const testRoutes = require("./test.routes");
const jobRoutes = require("./job/job.routes");
const simulationRoutes = require("./simulation/simulation.routes");
const authRoutes = require("./auth/auth.routes");
const dashboardRoutes = require("./dashboard/dashboard.routes");
const uploadRoutes = require("./upload/upload.routes");
const universeRoutes = require("./neural-universe/neural-universe.routes");

router.use("/test", testRoutes);
router.use("/job", jobRoutes);
router.use("/simulation", simulationRoutes);
router.use("/auth", authRoutes);
router.use("/dashboard", dashboardRoutes);
router.use("/upload", uploadRoutes);
router.use("/neural-universe", universeRoutes);

router.get("/", (req, res) => {
    res.json({ message: "API Root" });
});

module.exports = router;