const aiService = require("../../../integrations/ai.service");

module.exports = async (job, step, inputData) => {
    console.log("🎥 Video Processing step");
    console.log("📥 Input Data:", inputData);

    const result = await aiService.executeStep({
        jobId: job.data.jobId,
        step: step.name,
        inputData,
    });

    console.log("🤖 AI Result:", result);

    return result;
};