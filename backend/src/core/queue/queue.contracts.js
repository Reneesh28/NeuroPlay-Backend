// 🔥 Standard queue payload (v1)
const buildQueuePayload = ({ job, step, input_ref }) => {
    if (!job || !job.job_id) {
        throw new Error("Job with job_id is required for queue payload");
    }

    if (!step) {
        throw new Error("step is required for queue payload");
    }

    // 🔥 V1 CONTRACT ENFORCEMENT
    return {
        queue_version: "v1",
        job_id: job.job_id,
        context: {
            user_id: job.context.user_id,
            session_id: job.context.session_id,
            domain: job.context.domain,
            game_id: job.context.game_id,
            trace_id: job.context.trace_id,
            versions: job.context.versions
        },
        step: step,
        input_ref: input_ref || job.input_ref, // Use provided ref or fallback to initial
        input_type: "reference"
    };
};


module.exports = {
    buildQueuePayload
};