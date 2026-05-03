const aiService = require("../../../integrations/ai.service");
const { formatStepOutput, formatErrorOutput } = require("../../pipeline/output.formatter");

async function clusteringProcessor(job, inputData) {
    const step = "clustering";

    try {
        const start = Date.now();

        const response = await aiService.execute({
            job_id: job.job_id,
            step,
            input_ref: inputData,
            input_type: "ref", // 🔥 REQUIRED
            context: job.context,
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