const express = require("express");
const router = express.Router();
const controller = require("./dashboard.controller");
const { authMiddleware } = require("../../middleware/auth.middleware");

/**
 * 📊 DASHBOARD ENDPOINTS
 */

router.get("/:id", authMiddleware, controller.getDashboard);

module.exports = router;
