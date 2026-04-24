const { ErrorTypes } = require("./error.classifier");

/**
 * 🔥 RETRY MANAGER
 * Controls the retry strategy based on error classification.
 */

const RETRY_CONFIG = {
    MAX_RETRIES: 3,
    INITIAL_DELAY: 1000, // 1 second
    BACKOFF_FACTOR: 2    // Exponential
};

function shouldRetry(errorType, retryCount) {
    // Only TRANSIENT errors should be retried
    if (errorType !== ErrorTypes.TRANSIENT) {
        return false;
    }

    return retryCount < RETRY_CONFIG.MAX_RETRIES;
}

function getNextRetryDelay(retryCount) {
    return RETRY_CONFIG.INITIAL_DELAY * Math.pow(RETRY_CONFIG.BACKOFF_FACTOR, retryCount);
}

module.exports = {
    shouldRetry,
    getNextRetryDelay,
    RETRY_CONFIG
};
