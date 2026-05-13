const express = require("express");
const router = express.Router();
const controller = require("./simulation.controller");

const { validate } = require("../../middleware/validation.middleware");
const { baseRequestSchema } = require("../../schemas/base.schema");

const { authMiddleware } = require("../../middleware/auth.middleware");
const { simulationLimiter } = require("../../middleware/limiter.middleware");

router.post("/run", simulationLimiter, authMiddleware, validate(baseRequestSchema), controller.runSimulation);

module.exports = router;
