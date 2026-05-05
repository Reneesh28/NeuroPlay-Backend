const { v4: uuidv4 } = require("uuid");
const { PIPELINE_ORDER } = require("../pipeline/pipeline.config");

// 🔥 Immutable job creation (PIPELINE-DRIVEN)
const buildJob = ({ context, input_ref }) => {
    if (!context) {
        throw new Error("Context is required to build job");
    }

    if (!input_ref) {
        throw new Error("input_ref is required to build job");
    }

    // 🔥 TRACEABILITY: Auto-generate trace_id if missing
    if (!context.trace_id) {
        context.trace_id = `trc_${uuidv4().replace(/-/g, "")}`;
    }

    return {
        job_id: uuidv4(),

        context,

        status: "queued",

        // 🔥 First step from pipeline
        current_step: PIPELINE_ORDER[0],

        // 🔥 FULL PIPELINE STEPS
        steps: PIPELINE_ORDER.map((step, index) => ({
            name: step,
            status: "pending",

            // 🔥 Only first step gets input_ref
            input_ref: index === 0 ? input_ref : null,

            output_ref: null,

            execution_mode: "FULL",
            resolved_model_version: null,
            error: null
        })),

        input_ref,
        output_ref: null,

        total_steps_count: PIPELINE_ORDER.length,
        completed_steps_count: 0,
        progress: 0
    };

};

module.exports = { buildJob };