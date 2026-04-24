const queues = require("./queues");

/**
 * 🔥 Queue Router
 * Maps pipeline steps to their dedicated distributed queues
 */
function getQueueForStep(step) {
    switch (step) {
        case "video_processing":
            return queues.ingestionQueue;

        case "feature_extraction":
            return queues.processingQueue;

        case "embedding_generation":
        case "clustering":
            return queues.embeddingQueue;

        case "simulation":
            return queues.simulationQueue;


        default:
            console.warn(`⚠️ No specific queue for step: ${step}, falling back to default`);
            return queues.defaultQueue;
    }
}

module.exports = {
    getQueueForStep
};
