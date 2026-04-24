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

// 🔥 ATOMIC STEP UPDATE (STEP 4.2 FINAL)
async function updateStepStatus(jobId, stepName, updates) {

    // 🔥 Validate next_step (AI-driven)
    if (updates.next_step) {
        assertValidStep(updates.next_step);
    }

    // 🔥 Build safe $set query (NO undefined writes)
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

    // 🔥 STEP 4.2 — HEARTBEAT UPDATE (CRITICAL)
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

        // 🔥 FINAL STEP → COMPLETE JOB
        if (!updates.next_step) {
            setQuery.status = "completed";

            // 🔥 STEP 4 — mark finished time
            setQuery.finished_at = new Date();
        }
    }

    // 🔥 Increment query
    const incQuery = {};

    if (updates.status === "failed") {
        incQuery["steps.$.retries"] = 1;
    }

    // 🔥 Atomic update
    const job = await Job.findOneAndUpdate(
        { _id: jobId, "steps.name": stepName },
        {
            ...(Object.keys(setQuery).length > 0 && { $set: setQuery }),
            ...(Object.keys(incQuery).length > 0 && { $inc: incQuery })
        },
        { new: true }
    );

    if (!job) {
        throw new Error(`Job not found or step mismatch: ${jobId} / ${stepName}`);
    }

    // 🔥 SAFE progress calculation (derived, not stored blindly)
    const completedSteps = job.steps.filter(s => s.status === "completed").length;
    const totalSteps = job.steps.length;

    job.progress = Math.floor((completedSteps / totalSteps) * 100);

    // 🔥 Final aggregation
    if (job.status === "completed" && !job.output_ref) {
        job.output_ref = aggregateResults(job);
    }

    await job.save();

    return job;
}

module.exports = {
    createJob,
    updateJobStatus,
    updateStepStatus
};