module.exports = {
    video_processing: require("../workers/processors/ingestion.processor"),
    feature_extraction: require("../workers/processors/feature.processor"),
    embedding_generation: require("../workers/processors/embedding.processor"),
    memory_retrieval: require("../workers/processors/memory.processor"),

    simulation: require("../workers/processors/simulation.processor")
};