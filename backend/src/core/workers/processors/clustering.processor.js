const aiService = require("../../../integrations/ai.service");
const { formatStepOutput, formatErrorOutput } = require("../../pipeline/output.formatter");

async function clusteringProcessor(job) {
    const step = "clustering";

    try {
        const start = Date.now();

        const response = await aiService.execute({
            job_id: job._id,
            step,
            input: job.input_ref,
        });

        const executionTime = Date.now() - start;

        return formatStepOutput({
            step,
            rawOutput: response,
            executionTime,
        });

    } catch (error) {
        return formatErrorOutput({
            step,
            error,
        });
    }
}

module.exports = clusteringProcessor;