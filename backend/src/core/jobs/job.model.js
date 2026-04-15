const mongoose = require("mongoose");

const StepSchema = new mongoose.Schema({
    name: String,
    status: {
        type: String,
        enum: ["pending", "processing", "completed", "failed"],
        default: "pending",
    },
    retries: {
        type: Number,
        default: 0,
    },
    started_at: Date,
    completed_at: Date,
    error: {
        code: String,
        message: String,
    },
});

const JobSchema = new mongoose.Schema({
    user_id: {
        type: String,
        required: true,
    },

    type: {
        type: String,
        required: true,
    },

    status: {
        type: String,
        enum: ["queued", "processing", "completed", "failed"],
        default: "queued",
    },

    input_ref: {
        type: Object,
        required: true,
    },

    output_ref: {
        type: Object,
        default: null,
    },

    current_step: {
        type: String,
        default: null,
    },

    steps: [StepSchema],

    created_at: {
        type: Date,
        default: Date.now,
    },

    updated_at: {
        type: Date,
        default: Date.now,
    },
});

// 🔥 Performance index (important later)
JobSchema.index({ user_id: 1, created_at: -1 });

module.exports = mongoose.model("Job", JobSchema);