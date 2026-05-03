const { EXECUTION_MODES } = require("./constants/execution.constants");

/**
 * 🔥 Execution Mode Resolver
 * Ensures system NEVER upgrades execution mode
 * Only allows degradation: FULL → PARTIAL → FALLBACK
 */
function resolveNextExecutionMode(currentMode, stepMode) {
    if (!stepMode) return currentMode;

    // 🔥 Once FALLBACK, always FALLBACK
    if (currentMode === EXECUTION_MODES.FALLBACK) {
        return EXECUTION_MODES.FALLBACK;
    }

    // 🔥 PARTIAL can only stay PARTIAL or go to FALLBACK
    if (currentMode === EXECUTION_MODES.PARTIAL) {
        return stepMode === EXECUTION_MODES.FALLBACK
            ? EXECUTION_MODES.FALLBACK
            : EXECUTION_MODES.PARTIAL;
    }

    // 🔥 FULL can degrade
    return stepMode;
}

module.exports = {
    resolveNextExecutionMode
};