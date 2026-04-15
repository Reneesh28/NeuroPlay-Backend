function formatStepOutput({ step, rawOutput, executionTime }) {
    return {
        name: step,
        status: "completed",

        // 🔥 Extract only meaningful data from AI response
        output: rawOutput?.data || rawOutput || {},

        meta: {
            execution_time: executionTime || null,
            timestamp: Date.now(),
        },
    };
}

function formatErrorOutput({ step, error }) {
    return {
        name: step,
        status: "failed",

        error: {
            message: error.message,
            code: error.code || "STEP_ERROR",
        },

        meta: {
            timestamp: Date.now(),
        },
    };
}

module.exports = {
    formatStepOutput,
    formatErrorOutput,
};