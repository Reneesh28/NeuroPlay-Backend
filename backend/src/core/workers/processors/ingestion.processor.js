const aiService = require("../../../integrations/ai.service");
const { formatStepOutput, formatErrorOutput } = require("../../pipeline/output.formatter");

async function ingestionProcessor(job) {
    const step = "video_processing";

    try {
        const start = Date.now();

        // 🔥 Call AI service
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

module.exports = ingestionProcessor;