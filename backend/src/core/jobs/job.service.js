const Job = require("./job.model");
const { buildJob } = require("./job.builder");
const { assertValidTransition } = require("./job.state.machine");
const { aggregateResults } = require("../pipeline/result.aggregator");
const { assertValidStep } = require("../pipeline/step.validator");

// 🔥 Create deterministic job
async function createJob({ context, input_ref }) {
    if (!context) throw new Error("Context is required");
    if (!input_ref) throw new Error("input_ref is required");

    const jobData = buildJob({ context, input_ref });
    return await Job.create(jobData);
}

// 🔥 Update job status
async function updateJobStatus(jobId, nextStatus) {
    const job = await Job.findById(jobId);
    if (!job) throw new Error("Job not found");

    assertValidTransition(job.status, nextStatus);

    job.status = nextStatus;
    await job.save();

    return job;
}

// 🔥 ATOMIC STEP UPDATE
async function updateStepStatus(jobId, stepName, updates) {

    if (updates.next_step) {
        assertValidStep(updates.next_step);
    }

    const setQuery = {};

    if (updates.status !== undefined)
        setQuery["steps.$.status"] = updates.status;

    if (updates.output_ref !== undefined)
        setQuery["steps.$.output_ref"] = updates.output_ref;

    if (updates.execution_mode !== undefined)
        setQuery["steps.$.execution_mode"] = updates.execution_mode;

    if (updates.resolved_model_version !== undefined)
        setQuery["steps.$.resolved_model_version"] = updates.resolved_model_version;

    if (updates.error !== undefined)
        setQuery["steps.$.error"] = updates.error;

    // 🔥 heartbeat
    setQuery.last_heartbeat = new Date();

    // 🔥 Job-level updates
    if (updates.status === "processing") {
        setQuery.status = "processing";
    }

    if (updates.status === "failed") {
        setQuery.status = "failed";
    }

    if (updates.status === "completed") {
        setQuery.current_step = updates.next_step || null;

        if (!updates.next_step) {
            setQuery.status = "completed";
            setQuery.finished_at = new Date();
        }
    }

    const incQuery = {};

    if (updates.status === "failed") {
        incQuery["steps.$.retries"] = 1;
    }

    const job = await Job.findOneAndUpdate(
        { _id: jobId, "steps.name": stepName },
        {
            ...(Object.keys(setQuery).length > 0 && { $set: setQuery }),
            ...(Object.keys(incQuery).length > 0 && { $inc: incQuery })
        },
        { returnDocument: "after" }
    );

    if (!job) {
        throw new Error(`Job not found or step mismatch: ${jobId} / ${stepName}`);
    }

    // 🔥 Progress calc
    const completedSteps = job.steps.filter(s => s.status === "completed").length;
    const totalSteps = job.steps.length;
    job.progress = Math.floor((completedSteps / totalSteps) * 100);

    // 🔥 FINAL FIX — SAFE aggregation
    if (job.status === "completed" && !job.output_ref) {
        const aggregated = aggregateResults(job);

        job.output_ref =
            typeof aggregated === "string"
                ? aggregated
                : JSON.stringify(aggregated);
    }

    await job.save();

    return job;
}

module.exports = {
    createJob,
    updateJobStatus,
    updateStepStatus
};