const express = require("express");
const router = express.Router();
const controller = require("./simulation.controller");

router.post("/run", controller.runSimulation);

module.exports = router;
