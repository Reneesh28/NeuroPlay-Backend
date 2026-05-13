const express = require("express");
const router = express.Router();
const axios = require("axios");
const { authMiddleware } = require("../../middleware/auth.middleware");

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || "http://127.0.0.1:8000";

/**
 * 🧠 NEURAL UNIVERSE ENDPOINTS
 * Proxies requests to the AI engine's neural universe service.
 */

router.get("/map", authMiddleware, async (req, res) => {
    try {
        const response = await axios.get(`${AI_SERVICE_URL}/ai/neural-universe/map`, {
            headers: { 'x-trace-id': req.traceId || "unknown" }
        });
        res.json({ success: true, data: response.data });
    } catch (err) {
        console.error("Neural Universe Map Error:", err.message);
        res.status(500).json({ success: false, error: { message: "Failed to fetch neural universe map" } });
    }
});

router.get("/domain/:id", authMiddleware, async (req, res) => {
    try {
        const response = await axios.get(`${AI_SERVICE_URL}/ai/neural-universe/domain/${req.params.id}`, {
            headers: { 'x-trace-id': req.traceId || "unknown" }
        });
        res.json({ success: true, data: response.data });
    } catch (err) {
        console.error("Neural Universe Domain Error:", err.message);
        res.status(500).json({ success: false, error: { message: "Failed to fetch domain map" } });
    }
});

module.exports = router;
