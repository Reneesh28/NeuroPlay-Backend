const mongoose = require("mongoose");

/**
 * Behavior Snapshot Model — Phase 8: Persistent Digital Twin
 *
 * Periodic snapshots of player behavior for longitudinal trend analysis.
 * Generated every SNAPSHOT_INTERVAL simulations (default: 25).
 *
 * Storage Strategy:
 * - Each snapshot is lightweight (~500 bytes).
 * - Bounded to MAX_SNAPSHOTS_PER_USER (100) via TTL or manual cleanup.
 * - Indexed by (user_id, domain, created_at) for efficient trend queries.
 */

const BehaviorSnapshotSchema = new mongoose.Schema(
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

        // === SCORES AT SNAPSHOT TIME ===
        aggression_score: {
            type: Number,
            required: true,
            min: 0,
            max: 1
        },

        adaptability_score: {
            type: Number,
            required: true,
            min: 0,
            max: 1
        },

        // === AGGREGATE METRICS ===
        avg_confidence: {
            type: Number,
            default: 0.5,
            min: 0,
            max: 1
        },

        consistency_score: {
            type: Number,
            default: 0.5,
            min: 0,
            max: 1
        },

        // === CLUSTER DISTRIBUTION (snapshot copy) ===
        cluster_distribution: {
            type: Map,
            of: Number,
            default: {}
        },

        // === PREFERRED STYLE AT TIME ===
        preferred_style: {
            type: String,
            default: "unknown"
        },

        // === METADATA ===
        simulation_count: {
            type: Number,
            required: true
        },

        profile_version: {
            type: Number,
            required: true
        },

        // Snapshot sequence number for this user
        snapshot_number: {
            type: Number,
            required: true
        }
    },
    {
        timestamps: { createdAt: "created_at", updatedAt: false }
    }
);

// === INDEXES ===
// Efficient trend query: get last N snapshots for a user
BehaviorSnapshotSchema.index(
    { user_id: 1, domain: 1, created_at: -1 }
);

// Prevent unbounded growth: TTL index (90 days)
BehaviorSnapshotSchema.index(
    { created_at: 1 },
    { expireAfterSeconds: 90 * 24 * 60 * 60 }
);

module.exports = mongoose.model("BehaviorSnapshot", BehaviorSnapshotSchema);
