const videoProcessor = require("../workers/processors/video.processor");
const featureProcessor = require("../workers/processors/feature.processor");
const embeddingProcessor = require("../workers/processors/embedding.processor");
const clusteringProcessor = require("../workers/processors/clustering.processor");
const simulationProcessor = require("../workers/processors/simulation.processor");

module.exports = {
    video_processing: videoProcessor,
    feature_extraction: featureProcessor,
    embedding_generation: embeddingProcessor,
    clustering: clusteringProcessor,
    simulation: simulationProcessor,
};