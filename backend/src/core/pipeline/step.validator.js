const { PIPELINE_ORDER } = require("./pipeline.config");

// 🔥 Validate step exists
const assertValidStep = (stepName) => {
    if (!PIPELINE_ORDER.includes(stepName)) {
        const error = new Error(`Invalid step: ${stepName}`);
        error.code = "INVALID_STEP";
        error.statusCode = 400;
        throw error;
    }
};

// 🔥 Validate execution order
const assertStepOrder = (currentStep, nextStep) => {
    const currentIndex = PIPELINE_ORDER.indexOf(currentStep);
    const nextIndex = PIPELINE_ORDER.indexOf(nextStep);

    if (nextIndex !== currentIndex + 1) {
        const error = new Error(
            `Invalid step order: ${currentStep} → ${nextStep}`
        );
        error.code = "INVALID_STEP_ORDER";
        error.statusCode = 400;
        throw error;
    }
};

module.exports = {
    assertValidStep,
    assertStepOrder
};