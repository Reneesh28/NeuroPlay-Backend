const aiService = require("../../../integrations/ai.service");
const { formatStepOutput, formatErrorOutput } = require("../../pipeline/output.formatter");

async function featureProcessor(job, inputData) {
    const step = "feature_extraction";

    try {
        const start = Date.now();

        const response = await aiService.execute({
            job_id: job.job_id,
            step,
            input_ref: inputData,
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

module.exports = featureProcessor;