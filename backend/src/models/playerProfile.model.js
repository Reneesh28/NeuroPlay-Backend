const mongoose = require("mongoose");

/**
 * Player Profile Model — Phase 8: Persistent Digital Twin
 *
 * Stores persistent player identity across all sessions.
 * This is the CORE of the Digital Twin's long-term memory.
 *
 * Design:
 * - One profile per user_id (upsert pattern).
 * - Version increments on every meaningful update.
 * - cluster_distribution stores frequency counts (bounded by snapshot).
 * - Strengths/weaknesses are string tags derived from pattern extraction.
 * - Coaching history stores refs (not full objects) to avoid bloat.
 *
 * Storage Strategy:
 * - Profile itself is lightweight (~2KB per user).
 * - Detailed history lives in BehaviorSnapshot (separate collection).
 * - coaching_history_refs is bounded to last 50 entries.
 */

const MAX_COACHING_HISTORY = 50;
const MAX_STRENGTHS = 20;
const MAX_WEAKNESSES = 20;

const ConfidenceEntrySchema = new mongoose.Schema(
    {
        value: { type: Number, required: true, min: 0, max: 1 },
        timestamp: { type: Date, default: Date.now }
    },
    { _id: false }
);

const PlayerProfileSchema = new mongoose.Schema(
    {
        user_id: {
            type: String,
            required: true,
            unique: true,
            index: true
        },

        // === TACTICAL IDENTITY ===
        preferred_style: {
            type: String,
            enum: [
                "aggressive",
                "defensive",
                "flanking",
                "anchoring",
                "sniping",
                "support",
                "transition",
                "rush",
                "unknown"
            ],
            default: "unknown"
        },

        aggression_score: {
            type: Number,
            default: 0.5,
            min: 0,
            max: 1
        },

        adaptability_score: {
            type: Number,
            default: 0.5,
            min: 0,
            max: 1
        },

        // === CLUSTER DISTRIBUTION ===
        // Maps cluster_id (string key) → frequency count
        cluster_distribution: {
            type: Map,
            of: Number,
            default: {}
        },

        // === REACTION PROFILE ===
        reaction_profile: {
            avg_response_time: { type: Number, default: 0 },
            consistency_score: { type: Number, default: 0.5, min: 0, max: 1 },
            under_pressure_score: { type: Number, default: 0.5, min: 0, max: 1 }
        },

        // === STRENGTHS / WEAKNESSES ===
        strengths: {
            type: [String],
            default: [],
            validate: {
                validator: function (v) {
                    return v.length <= MAX_STRENGTHS;
                },
                message: `Strengths array cannot exceed ${MAX_STRENGTHS} entries`
            }
        },

        weaknesses: {
            type: [String],
            default: [],
            validate: {
                validator: function (v) {
                    return v.length <= MAX_WEAKNESSES;
                },
                message: `Weaknesses array cannot exceed ${MAX_WEAKNESSES} entries`
            }
        },

        // === CONFIDENCE HISTORY ===
        // Bounded rolling window of recent confidence scores
        confidence_history: {
            type: [ConfidenceEntrySchema],
            default: [],
            validate: {
                validator: function (v) {
                    return v.length <= 100;
                },
                message: "Confidence history cannot exceed 100 entries"
            }
        },

        // === COACHING HISTORY REFS ===
        // Stores output_ref strings pointing to coaching segments
        coaching_history_refs: {
            type: [String],
            default: [],
            validate: {
                validator: function (v) {
                    return v.length <= MAX_COACHING_HISTORY;
                },
                message: `Coaching history cannot exceed ${MAX_COACHING_HISTORY} entries`
            }
        },

        // === METADATA ===
        version: {
            type: Number,
            default: 1
        },

        total_simulations: {
            type: Number,
            default: 0
        },

        last_simulation_at: {
            type: Date,
            default: null
        },

        domain: {
            type: String,
            required: true,
            default: "blackops"
        }
    },
    {
        timestamps: true
    }
);

// === INDEXES ===
PlayerProfileSchema.index({ user_id: 1, domain: 1 }, { unique: true });

module.exports = mongoose.model("PlayerProfile", PlayerProfileSchema);
