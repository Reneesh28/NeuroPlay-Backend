const { v4: uuidv4 } = require("uuid");
const redis = require("../../config/redis");
const storageService = require("../../integrations/storage.service");
const jobService = require("../../core/jobs/job.service");
const producer = require("../../core/queue/producer");
const { normalizeInput } = require("../../core/pipeline/input.processor");


// 🔥 NEW IMPORTS
const { buildContext } = require("../../core/jobs/context.builder");
const { resolveDomain } = require("../../core/domain/domain.resolver");



const UPLOAD_PREFIX = "upload:";

async function initUpload(fileName, totalChunks) {
    const uploadId = uuidv4();
    const key = `${UPLOAD_PREFIX}${uploadId}`;

    await redis.set(
        key,
        JSON.stringify({
            fileName,
            totalChunks,
            receivedChunks: [],
            status: "initiated",
            createdAt: Date.now(),
        })
    );

    return { uploadId };
}

async function uploadChunk(uploadId, chunkIndex, buffer) {
    const key = `${UPLOAD_PREFIX}${uploadId}`;
    const raw = await redis.get(key);

    if (!raw) {
        const err = new Error("Upload session not found");
        err.code = "SESSION_NOT_FOUND";
        throw err;
    }

    let data;
    try {
        data = JSON.parse(raw);
    } catch (err) {
        const error = new Error("Corrupted upload session");
        error.code = "CORRUPTED_SESSION";
        throw error;
    }

    // 🔥 Validate chunk index
    if (chunkIndex < 0 || chunkIndex >= data.totalChunks) {
        const err = new Error("Invalid chunk index");
        err.code = "INVALID_CHUNK_INDEX";
        throw err;
    }

    await storageService.saveChunk(uploadId, chunkIndex, buffer);

    if (!data.receivedChunks.includes(chunkIndex)) {
        data.receivedChunks.push(chunkIndex);
    }

    await redis.set(key, JSON.stringify(data));

    return { received: data.receivedChunks.length };
}

async function completeUpload(uploadId, userId, game_id) {
    const key = `${UPLOAD_PREFIX}${uploadId}`;
    const raw = await redis.get(key);

    if (!raw) {
        const err = new Error("Upload session not found");
        err.code = "SESSION_NOT_FOUND";
        throw err;
    }

    let data;
    try {
        data = JSON.parse(raw);
    } catch (err) {
        const error = new Error("Corrupted upload session");
        error.code = "CORRUPTED_SESSION";
        throw error;
    }

    if (data.receivedChunks.length !== data.totalChunks) {
        const err = new Error("Not all chunks uploaded");
        err.code = "INCOMPLETE_UPLOAD";
        throw err;
    }

    // 🔥 STEP 1: Merge file
    const filePath = await storageService.mergeChunks(
        uploadId,
        data.totalChunks,
        data.fileName
    );

    // 🔥 STEP 2: Normalize input
    const normalizedInput = normalizeInput({
        file_path: filePath,
    });

    // 🔥 STEP 3: DOMAIN RESOLUTION (DYNAMIC)
    const domain = resolveDomain(game_id);

    // 🔥 STEP 4: BUILD CONTEXT
    const context = buildContext({
        user_id: userId,
        game_id,
        domain,
    });

    // 🔥 STEP 5: CREATE JOB
    const job = await jobService.createJob({
        context,
        input_ref: normalizedInput,
    });

    // 🔥 STEP 6: ENQUEUE JOB
    await producer.enqueueJobStep(job, job.current_step);


    // 🔥 STEP 8: CLEANUP
    await redis.del(key);

    return {
        jobId: job._id,
        filePath,
    };
}

module.exports = {
    initUpload,
    uploadChunk,
    completeUpload,
};