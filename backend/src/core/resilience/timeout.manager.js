/**
 * 🔥 TIMEOUT MANAGER
 * Manages step and job execution time limits.
 */

const TIMEOUT_CONFIG = {
    STEP_TIMEOUT: 60 * 1000,    // 60 seconds
    JOB_TIMEOUT: 10 * 60 * 1000, // 10 minutes
    STUCK_THRESHOLD: 5 * 60 * 1000 // 5 minutes without update
};

function isStepTimedOut(startTime) {
    const elapsed = Date.now() - startTime;
    return elapsed > TIMEOUT_CONFIG.STEP_TIMEOUT;
}

module.exports = {
    TIMEOUT_CONFIG,
    isStepTimedOut
};
