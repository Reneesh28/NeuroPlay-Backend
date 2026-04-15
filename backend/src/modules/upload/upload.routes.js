const express = require("express");
const multer = require("multer");
const controller = require("./upload.controller");

const router = express.Router();
const upload = multer();

router.post("/init", controller.init);
router.post("/chunk", upload.single("chunk"), controller.uploadChunk);
router.post("/complete", controller.complete);

module.exports = router;