const { successResponse, errorResponse } = require("../../contracts/api.contract");
const { resolveDomain } = require("../../core/domain/domain.resolver");
const { assertValidDomain } = require("../../core/domain/domain.validator");
const uploadService = require("./upload.service");

async function init(req, res, next) {
    try {
        const { user_id, game_id, payload } = req.validatedBody;

        // 🔥 STEP 1: Resolve domain (DO NOT TRUST USER)
        const domain = resolveDomain(game_id);

        // 🔥 STEP 2: Validate domain
        assertValidDomain(domain);

        // 🔥 TEMP: extract upload info
        const { fileName, totalChunks } = payload || {};

        const result = await uploadService.initUpload(fileName, totalChunks);

        return res.json(
            successResponse(result, {
                user_id,
                game_id,
                domain
            })
        );
    } catch (err) {
        next(err);
    }
}

async function uploadChunk(req, res, next) {
    try {
        const { uploadId, chunkIndex, game_id } = req.validatedBody;

        // 🔥 Resolve and validate domain
        const domain = resolveDomain(game_id);
        assertValidDomain(domain);

        const result = await uploadService.uploadChunk(
            uploadId,
            parseInt(chunkIndex),
            req.file.buffer
        );

        return res.json(
            successResponse(result, {
                uploadId,
                domain
            })
        );
    } catch (err) {
        next(err);
    }
}

async function complete(req, res, next) {
    try {
        const { user_id, game_id, payload } = req.validatedBody;
        const { uploadId } = payload || {};

        // 🔥 Resolve and validate domain
        const domain = resolveDomain(game_id);
        assertValidDomain(domain);

        const result = await uploadService.completeUpload(uploadId, user_id, game_id);

        return res.json(
            successResponse(result, {
                user_id,
                uploadId,
                domain
            })
        );
    } catch (err) {
        next(err);
    }
}

module.exports = {
    init,
    uploadChunk,
    complete,
};