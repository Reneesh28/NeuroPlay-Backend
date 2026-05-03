const queues = require("./queues");

/**
 * 🔥 Queue Router (FIXED)
 */
function getQueueForStep(step) {
    switch (step) {
        case "video_processing":
            return queues.ingestionQueue;

        case "feature_extraction":
            return queues.processingQueue;

        case "embedding_generation":
        case "memory_retrieval": // 🔥 FIXED
            return queues.embeddingQueue;

        case "simulation":
            return queues.simulationQueue;

        default:
            console.warn(`⚠️ No specific queue for step: ${step}, fallback`);
            return queues.defaultQueue;
    }
}

module.exports = {
    getQueueForStep
};