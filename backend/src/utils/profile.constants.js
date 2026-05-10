/**
 * Profile Constants — Phase 8: Persistent Digital Twin
 *
 * Centralized constants for the profile system.
 * Used by both the profile service and profile update processor.
 */

// === DEFAULT SCORES ===
const DEFAULT_AGGRESSION_SCORE = 0.5;
const DEFAULT_ADAPTABILITY_SCORE = 0.5;
const DEFAULT_CONSISTENCY_SCORE = 0.5;
const DEFAULT_UNDER_PRESSURE_SCORE = 0.5;

// === BOUNDS ===
const MAX_CONFIDENCE_HISTORY = 100;
const MAX_COACHING_HISTORY_REFS = 50;
const MAX_STRENGTHS = 20;
const MAX_WEAKNESSES = 20;

// === CLUSTER → STYLE MAPPING ===
// Mirrors CLUSTER_LABELS from ai-engine/app/pipeline/context_builder.py
const CLUSTER_STYLE_MAP = {
    0: "defensive",
    1: "aggressive",
    2: "flanking",
    3: "anchoring",
    4: "sniping",
    5: "support",
    6: "transition",
    7: "rush"
};

// === UPDATE PARAMETERS ===
// Exponential moving average alpha (0.1 = slow adaptation, 0.3 = fast)
const EMA_ALPHA = 0.15;

// === SNAPSHOT INTERVALS ===
// Generate a behavior snapshot every N simulations
const SNAPSHOT_INTERVAL = 25;

// Maximum snapshots per user (rolling window)
const MAX_SNAPSHOTS_PER_USER = 100;

module.exports = {
    DEFAULT_AGGRESSION_SCORE,
    DEFAULT_ADAPTABILITY_SCORE,
    DEFAULT_CONSISTENCY_SCORE,
    DEFAULT_UNDER_PRESSURE_SCORE,
    MAX_CONFIDENCE_HISTORY,
    MAX_COACHING_HISTORY_REFS,
    MAX_STRENGTHS,
    MAX_WEAKNESSES,
    CLUSTER_STYLE_MAP,
    EMA_ALPHA,
    SNAPSHOT_INTERVAL,
    MAX_SNAPSHOTS_PER_USER
};
