const mongoose = require("mongoose");

const SegmentSchema = new mongoose.Schema({
    user_id: {
        type: String,
        required: true,
    },

    session_id: {
        type: String,
        required: true,
    },

    domain: {
        type: String,
        required: true,
    },

    game_id: {
        type: String,
        required: true,
    },

    sequence_number: Number,

    // 🔥 CRITICAL ML INPUT
    ml_input: {
        feature_vector: {
            type: [Number],
            required: true,
        },
        feature_version: {
            type: String,
            required: true,
            default: "v1",
        },
    },

    created_at: {
        type: Date,
        default: Date.now,
    },
});

module.exports = mongoose.model("Segment", SegmentSchema);