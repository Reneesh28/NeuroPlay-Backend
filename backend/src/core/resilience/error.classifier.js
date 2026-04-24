/**
 * 🔥 ERROR CLASSIFIER
 * Unifies error intelligence across the pipeline.
 */

const ErrorTypes = {
    TRANSIENT: "TRANSIENT",   // Network issues, timeouts → Retry
    PERMANENT: "PERMANENT",   // Validation, Auth, 4xx → Fail
    ML_FAILURE: "ML_FAILURE", // AI Engine returned logic error → Fallback
    SYSTEM: "SYSTEM"          // Unhandled code errors → Fail
};

function classifyError(error) {
    if (!error) return ErrorTypes.SYSTEM;

    // 1. AI Service Errors (Axios)
    if (error.response) {
        const status = error.response.status;
        if (status === 400 || status === 422) return ErrorTypes.PERMANENT;
        if (status === 401 || status === 403) return ErrorTypes.PERMANENT;
        if (status >= 500) return ErrorTypes.TRANSIENT;
        return ErrorTypes.PERMANENT;
    }

    // 2. Network / Timeout Errors
    if (error.code === "ECONNABORTED" || error.code === "ETIMEDOUT") {
        return ErrorTypes.TRANSIENT;
    }

    if (error.request) {
        return ErrorTypes.TRANSIENT;
    }

    // 3. Validation Errors (Zod or Manual)
    if (error.name === "ValidationError" || error.is_validation) {
        return ErrorTypes.PERMANENT;
    }

    // 4. ML Specific Failures
    if (error.is_ml_error) {
        return ErrorTypes.ML_FAILURE;
    }

    return ErrorTypes.SYSTEM;
}

module.exports = {
    classifyError,
    ErrorTypes
};
