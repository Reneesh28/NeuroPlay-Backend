function formatStepOutput({ step, rawOutput, executionTime }) {
    return {
        status: "completed",

        // 🔥 Standardized output
        output: {
            step,
            data: rawOutput?.data ?? rawOutput ?? {},
            execution_time: executionTime ?? null,
            timestamp: Date.now(),
        },

        // 🔥 AI-DRIVEN CHAINING
        next_step: rawOutput?.next_step ?? null,

        // 🔥 AI-DRIVEN MODE
        execution_mode: rawOutput?.execution_mode ?? "FULL",

        // 🔥 VERSIONING
        model_version: rawOutput?.model_version ?? "v1"
    };
}


function formatErrorOutput({ step, error }) {
    let type = "SYSTEM";
    if (error.response) {
        type = error.response.status >= 500 ? "TRANSIENT" : "PERMANENT";
    } else if (error.request) {
        type = "TRANSIENT";
    }

    return {
        status: "failed",
        output: null,
        execution_mode: "FALLBACK",
        error: {
            message: error.message,
            code: error.code || "STEP_ERROR",
            type: type
        },
        model_version: null
    };
}


module.exports = {
    formatStepOutput,
    formatErrorOutput,
};