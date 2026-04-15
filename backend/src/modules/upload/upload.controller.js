const uploadService = require("./upload.service");

async function init(req, res, next) {
    try {
        const { fileName, totalChunks } = req.body;

        const result = await uploadService.initUpload(fileName, totalChunks);

        res.json({ success: true, data: result });
    } catch (err) {
        next(err);
    }
}

async function uploadChunk(req, res, next) {
    try {
        const { uploadId, chunkIndex } = req.body;

        const result = await uploadService.uploadChunk(
            uploadId,
            parseInt(chunkIndex),
            req.file.buffer
        );

        res.json({ success: true, data: result });
    } catch (err) {
        next(err);
    }
}

async function complete(req, res, next) {
    try {
        const { uploadId } = req.body;
        const userId = req.user?.id || "test_user";

        const result = await uploadService.completeUpload(uploadId, userId);

        res.json({ success: true, data: result });
    } catch (err) {
        next(err);
    }
}

module.exports = {
    init,
    uploadChunk,
    complete,
};