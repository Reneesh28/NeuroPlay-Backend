const express = require("express");
const multer = require("multer");
const controller = require("./upload.controller");

// 🔹 NEW IMPORTS (validation)
const { validate } = require("../../middleware/validation.middleware");
const { baseRequestSchema } = require("../../schemas/base.schema");

const router = express.Router();
const upload = multer();

const { authMiddleware } = require("../../middleware/auth.middleware");
const { uploadLimiter } = require("../../middleware/limiter.middleware");

router.post(
    "/init",
    uploadLimiter,
    authMiddleware,
    validate(baseRequestSchema),
    controller.init
);

const { prepareMultipartPayload } = require("../../middleware/multipart.middleware");

router.post(
    "/chunk",
    upload.single("chunk"),
    uploadLimiter,
    authMiddleware,
    prepareMultipartPayload(["uploadId", "chunkIndex"]),
    validate(baseRequestSchema),
    controller.uploadChunk
);

router.post(
    "/complete",
    uploadLimiter,
    authMiddleware,
    validate(baseRequestSchema),
    controller.complete
);

module.exports = router;