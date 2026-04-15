const { v4: uuidv4 } = require("uuid");
const redis = require("../../config/redis");
const storageService = require("../../integrations/storage.service");
const jobService = require("../../core/jobs/job.service");
const jobQueue = require("../../core/queue/job.queue"); // 🔥 NEW
const { normalizeInput } = require("../../core/pipeline/input.processor");

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
        throw new Error("Upload session not found");
    }

    let data;
    try {
        data = JSON.parse(raw);
    } catch (err) {
        throw new Error("Corrupted upload session");
    }

    // 🔥 Validate chunk index
    if (chunkIndex < 0 || chunkIndex >= data.totalChunks) {
        throw new Error("Invalid chunk index");
    }

    await storageService.saveChunk(uploadId, chunkIndex, buffer);

    if (!data.receivedChunks.includes(chunkIndex)) {
        data.receivedChunks.push(chunkIndex);
    }

    await redis.set(key, JSON.stringify(data));

    return { received: data.receivedChunks.length };
}

async function completeUpload(uploadId, userId) {
    const key = `${UPLOAD_PREFIX}${uploadId}`;
    const raw = await redis.get(key);

    if (!raw) {
        throw new Error("Upload session not found");
    }

    let data;
    try {
        data = JSON.parse(raw);
    } catch (err) {
        throw new Error("Corrupted upload session");
    }

    if (data.receivedChunks.length !== data.totalChunks) {
        throw new Error("Not all chunks uploaded");
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

    // 🔥 STEP 3: Create job
    const job = await jobService.createJob({
        user_id: userId,
        type: "video_processing",
        input_ref: normalizedInput,
    });

    // 🔥 STEP 4: PUSH TO QUEUE (CRITICAL)
    await jobQueue.add("processJob", {
        jobId: job._id.toString(),
    });

    // 🔥 STEP 5: Cleanup Redis
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