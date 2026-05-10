const PlayerProfile = require("../models/playerProfile.model");
const {
    DEFAULT_AGGRESSION_SCORE,
    DEFAULT_ADAPTABILITY_SCORE,
    MAX_CONFIDENCE_HISTORY,
    MAX_COACHING_HISTORY_REFS,
    CLUSTER_STYLE_MAP
} = require("../utils/profile.constants");

/**
 * Profile Service — Phase 8: Persistent Digital Twin
 *
 * CRUD operations for player profiles.
 * All methods are idempotent and safe for concurrent access.
 *
 * RULES:
 * - getOrCreate: Always returns a valid profile (creates default if missing).
 * - update: Uses findOneAndUpdate with $set to avoid race conditions.
 * - NEVER deletes profiles (soft-deactivation only if needed later).
 */

/**
 * Retrieves or creates a player profile.
 * Idempotent — safe to call on every simulation.
 */
async function getOrCreateProfile(userId, domain = "blackops") {
    if (!userId) throw new Error("user_id is required for profile lookup");

    let profile = await PlayerProfile.findOne({ user_id: userId, domain });

    if (!profile) {
        profile = await PlayerProfile.create({
            user_id: userId,
            domain,
            preferred_style: "unknown",
            aggression_score: DEFAULT_AGGRESSION_SCORE,
            adaptability_score: DEFAULT_ADAPTABILITY_SCORE,
            cluster_distribution: {},
            strengths: [],
            weaknesses: [],
            confidence_history: [],
            coaching_history_refs: [],
            version: 1,
            total_simulations: 0
        });

        console.log(`[Profile] Created new profile for user: ${userId}`);
    }

    return profile;
}

/**
 * Retrieves a player profile.
 * Returns null if not found (does not auto-create).
 */
async function getProfile(userId, domain = "blackops") {
    if (!userId) throw new Error("user_id is required");
    return await PlayerProfile.findOne({ user_id: userId, domain });
}

/**
 * Updates a player profile with new data.
 * Uses atomic $set to avoid race conditions.
 * Increments version on every update.
 */
async function updateProfile(userId, domain, updateData) {
    if (!userId) throw new Error("user_id is required for profile update");

    const result = await PlayerProfile.findOneAndUpdate(
        { user_id: userId, domain },
        {
            $set: updateData,
            $inc: { version: 1 }
        },
        { new: true, upsert: false }
    );

    if (!result) {
        throw new Error(`Profile not found for user: ${userId}, domain: ${domain}`);
    }

    return result;
}

/**
 * Appends a confidence entry to the rolling window.
 * Enforces MAX_CONFIDENCE_HISTORY bound.
 */
async function appendConfidence(userId, domain, confidenceValue) {
    const profile = await getOrCreateProfile(userId, domain);

    const entry = {
        value: Math.max(0, Math.min(1, confidenceValue)),
        timestamp: new Date()
    };

    // Bounded push — trim oldest if at capacity
    if (profile.confidence_history.length >= MAX_CONFIDENCE_HISTORY) {
        profile.confidence_history.shift();
    }

    profile.confidence_history.push(entry);
    await profile.save();

    return profile;
}

/**
 * Appends a coaching ref to the rolling window.
 * Enforces MAX_COACHING_HISTORY_REFS bound.
 */
async function appendCoachingRef(userId, domain, outputRef) {
    const profile = await getOrCreateProfile(userId, domain);

    if (profile.coaching_history_refs.length >= MAX_COACHING_HISTORY_REFS) {
        profile.coaching_history_refs.shift();
    }

    profile.coaching_history_refs.push(outputRef);
    await profile.save();

    return profile;
}

/**
 * Returns a lightweight profile summary suitable for injection
 * into the AI Engine context builder.
 */
function toProfileSummary(profile) {
    if (!profile) return null;

    return {
        user_id: profile.user_id,
        preferred_style: profile.preferred_style || "unknown",
        aggression_score: profile.aggression_score || 0.5,
        adaptability_score: profile.adaptability_score || 0.5,
        cluster_distribution: profile.cluster_distribution
            ? Object.fromEntries(profile.cluster_distribution)
            : {},
        reaction_profile: profile.reaction_profile || {},
        strengths: profile.strengths || [],
        weaknesses: profile.weaknesses || [],
        total_simulations: profile.total_simulations || 0,
        version: profile.version || 1
    };
}

module.exports = {
    getOrCreateProfile,
    getProfile,
    updateProfile,
    appendConfidence,
    appendCoachingRef,
    toProfileSummary
};
