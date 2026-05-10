const PlayerProfile = require("../models/playerProfile.model");
const BehaviorSnapshot = require("../models/behaviorSnapshot.model");
const PatternInsight = require("../models/patternInsight.model");

/**
 * Analytics Service — Phase 8: Persistent Digital Twin
 *
 * Provides analytics queries for player evolution tracking.
 *
 * RULES:
 * - All queries are bounded (max results, pagination support).
 * - Never exposes raw MongoDB documents — always format output.
 * - Read-only operations — never mutates data.
 */

/**
 * Returns the full profile evolution timeline for a player.
 *
 * @param {string} userId
 * @param {string} domain
 * @param {number} limit - Maximum snapshots to return (default: 50)
 */
async function getEvolutionTimeline(userId, domain = "blackops", limit = 50) {
    if (!userId) throw new Error("user_id is required");

    const snapshots = await BehaviorSnapshot.find({ user_id: userId, domain })
        .sort({ created_at: -1 })
        .limit(limit)
        .lean();

    return snapshots.map(s => ({
        snapshot_number: s.snapshot_number,
        simulation_count: s.simulation_count,
        aggression_score: s.aggression_score,
        adaptability_score: s.adaptability_score,
        avg_confidence: s.avg_confidence,
        preferred_style: s.preferred_style,
        created_at: s.created_at
    }));
}

/**
 * Returns the current profile with latest insights.
 */
async function getProfileAnalytics(userId, domain = "blackops") {
    if (!userId) throw new Error("user_id is required");

    const [profile, insights, recentSnapshots] = await Promise.all([
        PlayerProfile.findOne({ user_id: userId, domain }).lean(),
        PatternInsight.findOne({ user_id: userId, domain }).lean(),
        BehaviorSnapshot.find({ user_id: userId, domain })
            .sort({ created_at: -1 })
            .limit(5)
            .lean()
    ]);

    if (!profile) return null;

    return {
        profile: {
            user_id: profile.user_id,
            preferred_style: profile.preferred_style,
            aggression_score: profile.aggression_score,
            adaptability_score: profile.adaptability_score,
            total_simulations: profile.total_simulations,
            version: profile.version,
            last_simulation_at: profile.last_simulation_at
        },
        insights: insights ? {
            strengths: insights.strengths || [],
            weaknesses: insights.weaknesses || [],
            patterns: (insights.patterns || []).map(p => ({
                type: p.type,
                description: p.description,
                severity: p.severity
            })),
            data_quality: insights.data_quality
        } : null,
        recent_evolution: recentSnapshots.map(s => ({
            aggression_score: s.aggression_score,
            adaptability_score: s.adaptability_score,
            avg_confidence: s.avg_confidence,
            simulation_count: s.simulation_count,
            created_at: s.created_at
        }))
    };
}

/**
 * Returns aggregate statistics for a player.
 */
async function getPlayerStats(userId, domain = "blackops") {
    if (!userId) throw new Error("user_id is required");

    const profile = await PlayerProfile.findOne({ user_id: userId, domain }).lean();

    if (!profile) return null;

    // Compute confidence stats from history
    const confidenceValues = (profile.confidence_history || [])
        .map(c => c.value || 0)
        .filter(v => !isNaN(v));

    const avgConfidence = confidenceValues.length > 0
        ? confidenceValues.reduce((a, b) => a + b, 0) / confidenceValues.length
        : 0.5;

    const minConfidence = confidenceValues.length > 0
        ? Math.min(...confidenceValues)
        : 0;

    const maxConfidence = confidenceValues.length > 0
        ? Math.max(...confidenceValues)
        : 1;

    // Cluster distribution as sorted array
    const clusterDist = profile.cluster_distribution
        ? Object.fromEntries(profile.cluster_distribution)
        : {};

    return {
        user_id: profile.user_id,
        total_simulations: profile.total_simulations,
        aggression_score: profile.aggression_score,
        adaptability_score: profile.adaptability_score,
        preferred_style: profile.preferred_style,
        confidence: {
            average: Math.round(avgConfidence * 1000) / 1000,
            min: Math.round(minConfidence * 1000) / 1000,
            max: Math.round(maxConfidence * 1000) / 1000,
            samples: confidenceValues.length
        },
        cluster_distribution: clusterDist,
        strengths: profile.strengths || [],
        weaknesses: profile.weaknesses || [],
        profile_version: profile.version,
        last_simulation_at: profile.last_simulation_at
    };
}

module.exports = {
    getEvolutionTimeline,
    getProfileAnalytics,
    getPlayerStats
};
