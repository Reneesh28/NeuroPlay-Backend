const mongoose = require("mongoose");

const stepSchema = new mongoose.Schema({
    name: { type: String, required: true },

    status: {
        type: String,
        enum: ["pending", "processing", "completed", "failed"],
        default: "pending",
    },

    retries: { type: Number, default: 0 },

    started_at: Date,
    completed_at: Date,

    // 🔥 NEW: store AI output
    output: {
        type: Object,
        default: {},
    },

    error: {
        code: String,
        message: String,
    },
});

const jobSchema = new mongoose.Schema(
    {
        user_id: { type: String, required: true },
        session_id: { type: String },

        status: {
            type: String,
            enum: ["queued", "processing", "completed", "failed"],
            default: "queued",
        },

        steps: [stepSchema],

        created_at: { type: Date, default: Date.now },
        updated_at: { type: Date, default: Date.now },
    },
    { versionKey: false }
);

module.exports = mongoose.model("Job", jobSchema);