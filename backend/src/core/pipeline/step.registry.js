module.exports = {
    video_processing: require("../workers/processors/ingestion.processor"),
    feature_extraction: require("../workers/processors/feature.processor"),
    embedding_generation: require("../workers/processors/embedding.processor"),
    clustering: require("../workers/processors/clustering.processor"),
    simulation: require("../workers/processors/simulation.processor")
};