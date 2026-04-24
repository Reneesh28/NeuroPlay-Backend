const mongoose = require("mongoose");

const StepSchema = new mongoose.Schema(
    {
        name: { type: String, required: true },

        status: {
            type: String,
            enum: ["pending", "processing", "completed", "failed"],
            default: "pending"
        },

        input_ref: { type: Object },
        output_ref: { type: Object },

        execution_mode: {
            type: String,
            enum: ["FULL", "PARTIAL", "FALLBACK"],
            default: "FULL"
        },

        resolved_model_version: { type: String },

        retries: { type: Number, default: 0 },

        error: { type: Object }
    },
    { _id: false }
);

const JobSchema = new mongoose.Schema(
    {
        job_id: { type: String, required: true, unique: true },


        context: {
            user_id: { type: String, required: true },
            session_id: { type: String },

            game_id: { type: String, required: true },
            domain: { type: String, required: true },

            // 🔥 Grouped versions object
            versions: {
                model: { type: String },
                feature: { type: String },
                pipeline: { type: String }
            },

            trace_id: { type: String, required: true }
        },

        status: {
            type: String,
            enum: ["queued", "processing", "completed", "failed"],
            default: "queued"
        },

        current_step: { type: String },

        steps: [StepSchema],

        input_ref: { type: Object },
        output_ref: { type: Object },

        execution_mode: {
            type: String,
            enum: ["FULL", "PARTIAL", "FALLBACK"],
            default: "FULL"
        },
        total_steps_count: { type: Number, default: 0 },
        completed_steps_count: { type: Number, default: 0 },
        progress: { type: Number, default: 0 }


    },
    { timestamps: true }
);

module.exports = mongoose.model("Job", JobSchema);