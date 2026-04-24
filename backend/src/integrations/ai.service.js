const axios = require("axios");
const { VALID_EXECUTION_MODES } = require("../constants/execution.constants");
const { assertValidStep } = require("../pipeline/step.validator");

const AI_URL = process.env.AI_SERVICE_URL;

// 🔥 STRICT VALIDATION
function validateAIResponse(response) {
    if (!response || typeof response !== "object") {
        throw new Error("Invalid AI response");
    }

    if (!("output" in response)) {
        throw new Error("AI response missing output");
    }

    if (!("execution_mode" in response)) {
        throw new Error("AI response missing execution_mode");
    }

    if (!VALID_EXECUTION_MODES.includes(response.execution_mode)) {
        throw new Error(`Invalid execution_mode: ${response.execution_mode}`);
    }

    if (response.next_step !== null && response.next_step !== undefined) {
        assertValidStep(response.next_step);
    }

    return response;
}

async function execute(payload) {
    if (!AI_URL) {
        throw new Error("AI_SERVICE_URL not configured");
    }

    const { job_id, step, context } = payload;

    console.log(
        `📡 AI CALL [${step}] | Job:${job_id} | Trace:${context?.trace_id}`
    );

    const response = await axios.post(AI_URL, payload, {
        timeout: 30000 // 🔥 prevents hanging calls
    });

    return validateAIResponse(response.data);
}

module.exports = {
    execute,
};