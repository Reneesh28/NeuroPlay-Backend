const VALID_TRANSITIONS = {
    queued: ["processing"],

    processing: ["completed", "failed"],

    completed: [],
    failed: []
};

const assertValidTransition = (currentStatus, nextStatus) => {
    const allowed = VALID_TRANSITIONS[currentStatus] || [];

    if (!allowed.includes(nextStatus)) {
        const error = new Error(
            `Invalid state transition: ${currentStatus} → ${nextStatus}`
        );
        error.code = "INVALID_JOB_TRANSITION";
        error.statusCode = 400;
        throw error;
    }
};

module.exports = {
    assertValidTransition
};