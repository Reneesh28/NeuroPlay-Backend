const express = require("express");
const multer = require("multer");
const controller = require("./upload.controller");

// 🔹 NEW IMPORTS (validation)
const { validate } = require("../../middleware/validation.middleware");
const { baseRequestSchema } = require("../../schemas/base.schema");

const router = express.Router();
const upload = multer();

router.post(
    "/init",
    validate(baseRequestSchema),
    controller.init
);

router.post(
    "/chunk",
    upload.single("chunk"),
    validate(baseRequestSchema),
    controller.uploadChunk
);

router.post(
    "/complete",
    validate(baseRequestSchema),
    controller.complete
);

module.exports = router;