const express = require("express");
const router = express.Router();

const testRoutes = require("./test.routes");
const jobRoutes = require("./job.routes");

router.use("/test", testRoutes);
router.use("/job", jobRoutes);

router.get("/", (req, res) => {
    res.json({ message: "API Root" });
});

module.exports = router;