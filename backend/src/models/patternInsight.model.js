const mongoose = require("mongoose");

/**
 * Pattern Insight Model — Phase 8: Persistent Digital Twin
 *
 * Stores extracted behavioral patterns and insights for a player.
 * Updated periodically by the pattern extraction engine.
 *
 * Design:
 * - One document per user per domain (upsert pattern).
 * - Strengths/weaknesses/patterns are overwritten on each update
 *   (not appended) to prevent unbounded growth.
 * - last_computed_at tracks staleness.
 */

const PatternDetailSchema = new mongoose.Schema(
    {
        type: {
            type: String,
            required: true,
            enum: [
                "over_reliance",
                "tactical_gap",
                "high_risk_habit",
                "overly_passive",
                "low_confidence",
                "unstable_confidence",
                "behavioral_loop",
                "other"
            ]
        },

        description: {
            type: String,
            required: true,
            maxlength: 300
        },

        frequency: {
            type: Number,
            default: 0
        },

        severity: {
            type: String,
            enum: ["low", "medium", "high"],
            default: "low"
        }
    },
    { _id: false }
);

const PatternInsightSchema = new mongoose.Schema(
    {
        user_id: {
            type: String,
            required: true,
            index: true
        },

        domain: {
            type: String,
            required: true,
            default: "blackops"
        },

        // === EXTRACTED INSIGHTS ===
        strengths: {
            type: [String],
            default: [],
            validate: {
                validator: function (v) {
                    return v.length <= 20;
                },
                message: "Strengths cannot exceed 20 entries"
            }
        },

        weaknesses: {
            type: [String],
            default: [],
            validate: {
                validator: function (v) {
                    return v.length <= 20;
                },
                message: "Weaknesses cannot exceed 20 entries"
            }
        },

        patterns: {
            type: [PatternDetailSchema],
            default: [],
            validate: {
                validator: function (v) {
                    return v.length <= 30;
                },
                message: "Patterns cannot exceed 30 entries"
            }
        },

        // === QUALITY ===
        data_quality: {
            type: String,
            enum: ["sufficient", "insufficient", "error"],
            default: "insufficient"
        },

        // === METADATA ===
        last_computed_at: {
            type: Date,
            default: Date.now
        },

        based_on_simulations: {
            type: Number,
            default: 0
        }
    },
    {
        timestamps: true
    }
);

// === INDEXES ===
PatternInsightSchema.index({ user_id: 1, domain: 1 }, { unique: true });

module.exports = mongoose.model("PatternInsight", PatternInsightSchema);
