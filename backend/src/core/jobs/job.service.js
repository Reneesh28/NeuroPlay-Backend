const Job = require("./job.model");
const { PIPELINE_STEPS } = require("../pipeline/step.constants");

async function createJob({ user_id, type, input_ref }) {
    console.log("PIPELINE_STEPS:", PIPELINE_STEPS);

    const steps = PIPELINE_STEPS.map(step => ({
        name: step,
        status: "pending",
        retries: 0,
    }));

    const job = new Job({
        user_id,
        type,
        input_ref,
        status: "queued",
        steps,
        current_step: steps[0]?.name || null,
        created_at: new Date(),
        updated_at: new Date(),
    });

    await job.save();

    return job;
}

module.exports = {
    createJob,
};