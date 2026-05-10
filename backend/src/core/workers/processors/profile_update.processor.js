const PlayerProfile = require("../../../models/playerProfile.model");
const { toProfileSummary } = require("../../../services/profile.service");
const {
    EMA_ALPHA,
    CLUSTER_STYLE_MAP,
    MAX_CONFIDENCE_HISTORY
} = require("../../../utils/profile.constants");

/**
 * Profile Update Processor — Phase 8: Persistent Digital Twin
 *
 * Triggered AFTER the simulation step completes.
 * Receives simulation output and updates the player profile in MongoDB.
 *
 * This is a BACKEND-SIDE processor that:
 * 1. Reads the simulation result from the job.
 * 2. Fetches (or creates) the player profile.
 * 3. Applies EMA-based score updates.
 * 4. Persists the updated profile.
 *
 * RULES:
 * - NEVER crashes the pipeline — all errors are caught and logged.
 * - Idempotent — safe to re-run on the same job.
 * - Bounded writes — confidence_history is capped.
 */

/**
 * Process a completed simulation job and update the player profile.
 *
 * @param {Object} job - The completed Job document.
 * @param {Object} simulationResult - The simulation step output.
 */
async function processProfileUpdate(job, simulationResult) {
    const userId = job?.context?.user_id;
    const domain = job?.context?.domain || "blackops";
    const traceId = job?.context?.trace_id || "unknown";

    if (!userId) {
        console.warn(`[Trace:${traceId}] [ProfileUpdate] Missing user_id — skipping`);
        return null;
    }

    try {
        // === 1. GET OR CREATE PROFILE ===
        let profile = await PlayerProfile.findOne({ user_id: userId, domain });

        if (!profile) {
            profile = await PlayerProfile.create({
                user_id: userId,
                domain,
                preferred_style: "unknown",
                aggression_score: 0.5,
                adaptability_score: 0.5,
                cluster_distribution: {},
                strengths: [],
                weaknesses: [],
                confidence_history: [],
                coaching_history_refs: [],
                version: 1,
                total_simulations: 0
            });

            console.log(`[Trace:${traceId}] [ProfileUpdate] Created new profile for ${userId}`);
        }

        // === 2. EXTRACT SIMULATION DATA ===
        const action = simulationResult?.predicted_action || "hold position";
        const confidence = parseFloat(simulationResult?.confidence || 0.5);
        const executionMode = simulationResult?.execution_mode || "FULL";

        // === 3. COMPUTE AGGRESSION UPDATE (EMA) ===
        const aggressionSignal = computeAggressionSignal(action);
        const newAggression = ema(
            profile.aggression_score || 0.5,
            aggressionSignal
        );

        // === 4. APPEND CONFIDENCE TO ROLLING WINDOW ===
        const confidenceEntry = {
            value: Math.max(0, Math.min(1, confidence)),
            timestamp: new Date()
        };

        let confidenceHistory = [...(profile.confidence_history || [])];
        if (confidenceHistory.length >= MAX_CONFIDENCE_HISTORY) {
            confidenceHistory = confidenceHistory.slice(-MAX_CONFIDENCE_HISTORY + 1);
        }
        confidenceHistory.push(confidenceEntry);

        // === 5. UPDATE PROFILE ===
        const updateResult = await PlayerProfile.findOneAndUpdate(
            { user_id: userId, domain },
            {
                $set: {
                    aggression_score: round4(newAggression),
                    confidence_history: confidenceHistory,
                    last_simulation_at: new Date()
                },
                $inc: {
                    version: 1,
                    total_simulations: 1
                }
            },
            { new: true }
        );

        console.log(
            `[Trace:${traceId}] [ProfileUpdate] Updated | ` +
            `User: ${userId} | ` +
            `Aggression: ${profile.aggression_score?.toFixed(3)} → ${round4(newAggression)} | ` +
            `Sims: ${updateResult.total_simulations}`
        );

        return updateResult;

    } catch (error) {
        console.error(
            `[Trace:${traceId}] [ProfileUpdate] ERROR: ${error.message}`
        );
        return null; // Never crash the pipeline
    }
}

// === HELPERS ===

const AGGRESSIVE_KEYWORDS = ["push", "rush", "flank", "attack", "engage", "peek", "entry"];
const DEFENSIVE_KEYWORDS = ["hold", "retreat", "rotate", "fall back", "anchor", "defend"];

function computeAggressionSignal(action) {
    const lower = (action || "").toLowerCase().trim();

    for (const kw of AGGRESSIVE_KEYWORDS) {
        if (lower.includes(kw)) return 0.85;
    }

    for (const kw of DEFENSIVE_KEYWORDS) {
        if (lower.includes(kw)) return 0.2;
    }

    return 0.5;
}

function ema(current, newValue, alpha = EMA_ALPHA) {
    return Math.max(0, Math.min(1, current * (1 - alpha) + newValue * alpha));
}

function round4(val) {
    return Math.round(val * 10000) / 10000;
}

module.exports = {
    processProfileUpdate
};
