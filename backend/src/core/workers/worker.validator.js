const { assertValidStep } = require("../pipeline/step.validator");

/**
 * 🔥 Worker Payload Validator (v1)
 * Enforces strict job contract before execution
 */
function validateWorkerPayload(payload) {
    if (!payload) {
        throw new Error("Empty payload received from queue");
    }

    // 1. Version Check
    if (payload.queue_version !== "v1") {
        throw new Error(`Unsupported queue version: ${payload.queue_version}`);
    }

    // 2. Identity Check
    if (!payload.job_id) {
        throw new Error("Missing job_id in payload");
    }

    // 3. Step Check
    if (!payload.step) {
        throw new Error("Missing step name in payload");
    }
    assertValidStep(payload.step);

    // 4. Context Check (Mandatory Fields)
    const { context } = payload;
    if (!context) {
        throw new Error("Missing context in payload");
    }

    const requiredContextFields = ["user_id", "domain", "game_id", "trace_id"];
    for (const field of requiredContextFields) {
        if (!context[field]) {
            throw new Error(`Missing mandatory context field: ${field}`);
        }
    }

    // 5. Input Check
    if (!payload.input_ref) {
        throw new Error("Missing input_ref in payload");
    }

    return true;
}

module.exports = {
    validateWorkerPayload
};
