const axios = require("axios");
const { VALID_EXECUTION_MODES } = require("../core/constants/execution.constants");
const { assertValidStep } = require("../core/pipeline/step.validator");

const AI_BASE_URL = process.env.AI_SERVICE_URL;

// ==============================
// 🔥 STEP → ENDPOINT MAPPING
// ==============================
const STEP_ENDPOINT_MAP = {
    embedding_generation: "/ai/embedding-generation",
    memory_retrieval: "/ai/memory-retrieval",
    simulation: "/ai/execute"
};

// ==============================
// 🔥 CONTEXT NORMALIZATION (CRITICAL FIX)
// ==============================
function normalizeContext(context = {}) {
    return {
        ...context,

        // 🔥 Ensure required fields exist
        feature_version:
            context.feature_version || context?.versions?.feature || "v1",

        pipeline_version:
            context.pipeline_version || context?.versions?.pipeline || "v1",

        resolved_model_version:
            context.resolved_model_version || context?.versions?.model || "v1"
    };
}

// ==============================
// 🔥 NORMALIZE + VALIDATE RESPONSE
// ==============================
function normalizeAIResponse(response) {
    if (!response || typeof response !== "object") {
        throw new Error("Invalid AI response");
    }

    if (!("output_ref" in response)) {
        throw new Error("AI response missing output_ref");
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

    return {
        status: "completed",
        output: response.output_ref,
        next_step: response.next_step || null,
        execution_mode: response.execution_mode,
        model_version: response.resolved_model_version || null
    };
}

// ==============================
// 🔥 ENDPOINT RESOLUTION
// ==============================
function resolveEndpoint(step) {
    const endpoint = STEP_ENDPOINT_MAP[step] || "/ai/execute";

    // Prevent double /ai prefix
    if (endpoint.startsWith("/ai") && AI_BASE_URL.endsWith("/ai")) {
        return endpoint.replace("/ai", "");
    }

    return endpoint;
}

// ==============================
// 🚀 MAIN EXECUTION
// ==============================
async function execute(payload) {
    if (!AI_BASE_URL) {
        throw new Error("AI_SERVICE_URL not configured");
    }

    const { job_id, step } = payload;

    // 🔥 FIX: normalize context BEFORE sending
    const context = normalizeContext(payload.context);

    const endpoint = resolveEndpoint(step);

    console.log(
        `📡 AI CALL [${step}] → ${endpoint} | Job:${job_id} | Trace:${context?.trace_id}`
    );

    try {
        const response = await axios.post(
            `${AI_BASE_URL}${endpoint}`,
            {
                ...payload,
                context // 🔥 send normalized context
            },
            { timeout: 30000 }
        );

        console.log("🔥 AI RAW RESPONSE:", response.data); // debug

        return normalizeAIResponse(response.data);

    } catch (error) {
        console.error("❌ AI SERVICE ERROR:", {
            step,
            endpoint,
            message: error.message,
            response: error.response?.data
        });

        return {
            status: "completed",
            output: null,
            next_step: null,
            execution_mode: "FALLBACK",
            model_version: null
        };
    }
}

module.exports = {
    execute,
};