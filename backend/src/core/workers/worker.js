const Job = require("../jobs/job.model");

const ingestionProcessor = require("./processors/ingestion.processor");
const featureProcessor = require("./processors/feature.processor");
const embeddingProcessor = require("./processors/embedding.processor");
const clusteringProcessor = require("./processors/clustering.processor");
const simulationProcessor = require("./processors/simulation.processor");

const { aggregateResults } = require("../pipeline/result.aggregator");

async function processJob(jobId) {
    const job = await Job.findById(jobId);

    if (!job) throw new Error("Job not found");

    job.status = "processing";

    while (job.current_step) {
        const currentStep = job.current_step;

        let result;

        try {
            switch (currentStep) {

                case "video_processing":
                    result = await ingestionProcessor(job);
                    break;

                case "feature_extraction":
                    result = await featureProcessor(job);
                    break;

                case "embedding_generation":
                    result = await embeddingProcessor(job);
                    break;

                case "clustering":
                    result = await clusteringProcessor(job);
                    break;

                case "simulation":
                    result = await simulationProcessor(job);
                    break;

                default:
                    throw new Error(`Unknown step: ${currentStep}`);
            }

            const stepIndex = job.steps.findIndex(s => s.name === currentStep);

            if (stepIndex === -1) {
                throw new Error(`Step not found in job.steps: ${currentStep}`);
            }

            // 🔥 SAFE MONGOOSE UPDATE (CRITICAL FIX)
            const stepDoc = job.steps[stepIndex];

            stepDoc.status = result.status;

            if (result.output !== undefined) {
                stepDoc.output = result.output;
            }

            if (result.error !== undefined) {
                stepDoc.error = result.error;
            }

            if (result.meta !== undefined) {
                stepDoc.meta = result.meta;
            }

            // 🔥 MOVE TO NEXT STEP
            const nextStep = job.steps[stepIndex + 1];

            if (nextStep) {
                job.current_step = nextStep.name;
            } else {
                job.current_step = null;
                job.status = "completed";

                // 🔥 FINAL AGGREGATION
                job.output_ref = aggregateResults(job);
            }

        } catch (error) {
            const stepIndex = job.steps.findIndex(s => s.name === currentStep);

            if (stepIndex !== -1) {
                const stepDoc = job.steps[stepIndex];

                stepDoc.status = "failed";
                stepDoc.error = {
                    message: error.message,
                };
            }

            job.status = "failed";
            job.current_step = null;
        }

        job.updated_at = new Date();
        await job.save();
    }

    return job;
}

module.exports = {
    processJob,
};