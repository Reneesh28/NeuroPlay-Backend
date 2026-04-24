// 🔥 Standard queue payload (v1)
// STRICT CONTRACT — NO FALLBACKS, NO IMPLICIT BEHAVIOR

const buildQueuePayload = ({ job, step, input_ref }) => {
    // 1. Validate job
    if (!job || !job.job_id) {
        throw new Error("Job with job_id is required for queue payload");
    }

    // 2. Validate step
    if (!step) {
        throw new Error("step is required for queue payload");
    }

    // 3. 🔥 STRICT: input_ref MUST be explicitly provided
    if (!input_ref) {
        throw new Error(`input_ref is REQUIRED for step: ${step}`);
    }

    // 4. Validate context (defensive check)
    if (!job.context) {
        throw new Error("Job context is missing");
    }

    const {
        user_id,
        session_id,
        domain,
        game_id,
        trace_id,
        versions
    } = job.context;

    if (!user_id || !domain || !game_id || !trace_id) {
        throw new Error("Invalid job context: missing required fields");
    }

    // 5. Build payload
    return {
        queue_version: "v1",

        job_id: job.job_id,

        context: {
            user_id,
            session_id,
            domain,
            game_id,
            trace_id,
            versions
        },

        step: step,

        // 🔥 Deterministic input — NO fallback
        input_ref: input_ref,

        input_type: "reference"
    };
};

module.exports = {
    buildQueuePayload
};