const { ErrorTypes } = require("./error.classifier");
const { EXECUTION_MODES } = require("../constants/execution.constants");

const RETRY_CONFIG = {
    MAX_RETRIES: 3,
    INITIAL_DELAY: 1000,
    BACKOFF_FACTOR: 2
};

function shouldRetry(errorType, retryCount, executionMode = EXECUTION_MODES.FULL) {

    if (executionMode === EXECUTION_MODES.FALLBACK) return false;

    if (errorType === ErrorTypes.ML_FAILURE) return false;

    if (errorType === ErrorTypes.PERMANENT) return false;

    if (errorType === ErrorTypes.TRANSIENT) {
        return retryCount < RETRY_CONFIG.MAX_RETRIES;
    }

    return false;
}

function getNextRetryDelay(retryCount) {
    return RETRY_CONFIG.INITIAL_DELAY * Math.pow(RETRY_CONFIG.BACKOFF_FACTOR, retryCount);
}

module.exports = {
    shouldRetry,
    getNextRetryDelay,
    RETRY_CONFIG
};