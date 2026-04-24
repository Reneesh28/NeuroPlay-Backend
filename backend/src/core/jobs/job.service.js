const Job = require("./job.model");
const { buildJob } = require("./job.builder");
const { assertValidTransition } = require("./job.state.machine");
const { aggregateResults } = require("../pipeline/result.aggregator");

// 🔥 Create deterministic job
async function createJob({ context, input_ref }) {
    if (!context) {
        throw new Error("Context is required for job creation");
    }

    if (!input_ref) {
        throw new Error("input_ref is required for job creation");
    }

    const jobData = buildJob({
        context,
        input_ref
    });

    const job = await Job.create(jobData);

    return job;
}

// 🔥 Update job status (STATE MACHINE ENFORCED)
async function updateJobStatus(jobId, nextStatus) {
    const job = await Job.findById(jobId);

    if (!job) {
        throw new Error("Job not found");
    }

    // 🔥 Validate transition
    assertValidTransition(job.status, nextStatus);

    job.status = nextStatus;

    await job.save();

    return job;
}


// 🔥 Update step status (CRITICAL for pipeline - ATOMIC)
async function updateStepStatus(jobId, stepName, updates) {
    const setQuery = {
        "steps.$.status": updates.status,
        "steps.$.output_ref": updates.output_ref,
        "steps.$.execution_mode": updates.execution_mode,
        "steps.$.resolved_model_version": updates.resolved_model_version,
        "steps.$.error": updates.error
    };

    const incQuery = {};

    // 1. Handle Job Status & Next Step
    if (updates.status === "processing") {
        setQuery.status = "processing";
    }

    if (updates.status === "failed") {
        setQuery.status = "failed";
        incQuery["steps.$.retries"] = 1;
    }

    if (updates.status === "completed") {
        setQuery.current_step = updates.next_step || null;
        incQuery.completed_steps_count = 1;

        if (!updates.next_step) {
            setQuery.status = "completed";
        }
    }

    // 2. Atomic Update
    const job = await Job.findOneAndUpdate(
        { _id: jobId, "steps.name": stepName },
        { 
            $set: setQuery,
            ...(Object.keys(incQuery).length > 0 ? { $inc: incQuery } : {})
        },
        { new: true }
    );

    if (!job) {
        throw new Error(`Job not found or step mismatch: ${jobId} / ${stepName}`);
    }

    // 3. Recalculate progress (can be done after atomic update)
    job.progress = Math.floor((job.completed_steps_count / job.total_steps_count) * 100);
    
    // 4. Final Aggregation if complete
    if (job.status === "completed" && !job.output_ref) {
        job.output_ref = aggregateResults(job);
    }

    await job.save(); // Save the recalculated fields

    return job;
}




module.exports = {
    createJob,
    updateJobStatus,
    updateStepStatus
};