const jobService = require("../../jobs/job.service");
const stepRegistry = require("../../pipeline/step.registry");

module.exports = async (job) => {
    const { jobId } = job.data;

    console.log("⚙️ Processing job:", job.name);

    // 1. Get job from DB
    let dbJob = await jobService.getJob(jobId);

    if (!dbJob) {
        throw new Error("Job not found");
    }

    // 2. Mark job as processing
    await jobService.updateJobStatus(jobId, "processing");

    // 3. Loop through steps (WITH DATA FLOW)
    for (let i = 0; i < dbJob.steps.length; i++) {
        const step = dbJob.steps[i];

        if (step.status === "completed") continue;

        console.log(`➡️ Executing step: ${step.name}`);

        const processor = stepRegistry[step.name];

        if (!processor) {
            throw new Error(`No processor found for step: ${step.name}`);
        }

        // 🔥 Get previous step output
        const inputData =
            i === 0
                ? job.data.inputData || {}   // 🔥 FIRST STEP uses USER INPUT
                : dbJob.steps[i - 1]?.output || {};

        // Mark step as processing
        await jobService.updateStep(jobId, step.name, {
            status: "processing",
            started_at: new Date(),
        });

        // 🔥 Execute step with inputData
        const result = await processor(job, step, inputData);

        // 🔥 Store output
        await jobService.updateStep(jobId, step.name, {
            status: "completed",
            completed_at: new Date(),
            output: result?.output || {},
        });

        // 🔥 Refresh job state (VERY IMPORTANT)
        dbJob = await jobService.getJob(jobId);
    }

    // 4. Mark job as completed
    await jobService.updateJobStatus(jobId, "completed");

    console.log("✅ Full pipeline completed:", jobId);

    return { success: true };
};