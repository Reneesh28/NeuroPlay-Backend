const mongoose = require("mongoose");

const SegmentSchema = new mongoose.Schema({
    ref: {
        type: String,
        required: true,
        index: true
    },

    domain: {
        type: String,
        required: true,
        index: true
    },

    trace_id: String,
    step: String,
    input_ref: mongoose.Schema.Types.Mixed,

    // 🔥 THE CORE DATA PAYLOAD
    data: {
        type: mongoose.Schema.Types.Mixed,
        required: true
    },

    // Legacy / Extended fields (keeping for compatibility)
    user_id: String,
    session_id: String,
    game_id: String,
    sequence_number: Number,

    ml_input: {
        feature_vector: [Number],
        feature_version: String
    },

    created_at: {
        type: Date,
        default: Date.now,
    },
}, { 
    strict: false, // 🔥 Allow fields not in schema (crucial for AI output)
    timestamps: { createdAt: 'created_at', updatedAt: false }
});

module.exports = mongoose.model("Segment", SegmentSchema);