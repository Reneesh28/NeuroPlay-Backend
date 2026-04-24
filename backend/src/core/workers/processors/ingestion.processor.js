const aiService = require("../../../integrations/ai.service");
const { formatStepOutput, formatErrorOutput } = require("../../pipeline/output.formatter");

async function ingestionProcessor(job, inputData) {
    const step = "video_processing";

    try {
        const start = Date.now();

        // 🔥 Call AI service (Strict Contract)
        const response = await aiService.execute({
            job_id: job.job_id,
            step,
            input_ref: inputData, // Always a reference
            context: job.context,  // Propagate full context
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

module.exports = ingestionProcessor;