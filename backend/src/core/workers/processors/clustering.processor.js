const aiService = require("../../../integrations/ai.service");

module.exports = async (job, step, inputData) => {
    console.log("📦 Clustering step");
    console.log("📥 Input Data:", inputData);

    const result = await aiService.executeStep({
        jobId: job.data.jobId,
        step: step.name,
        inputData,
    });

    return result;
};