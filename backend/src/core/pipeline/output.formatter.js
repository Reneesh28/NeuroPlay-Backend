const { classifyError } = require("../resilience/error.classifier");

function formatStepOutput({ step, rawOutput, executionTime }) {
    // 🔥 FIX: allow objects or strings (rich metadata support)
    const safeOutput =
        (typeof rawOutput?.output === "string" || typeof rawOutput?.output === "object")
            ? rawOutput.output
            : null;

    return {
        status: "completed",
        output: safeOutput,

        next_step: rawOutput?.next_step ?? null,

        execution_mode: rawOutput?.execution_mode ?? "FULL",

        model_version: rawOutput?.model_version ?? "v1"
    };
}

function formatErrorOutput({ step, error }) {
    const type = classifyError(error);

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