const Job = require("../../core/jobs/job.model");
const PlayerProfile = require("../../models/playerProfile.model");
const PatternInsight = require("../../models/patternInsight.model");
const { successResponse, errorResponse } = require("../../contracts/api.contract");
const Segment = require("../../core/database/mongo/collections/segment.collection");

/**
 * 📊 GET DASHBOARD DATA
 * Aggregates data for a specific simulation run (job).
 */
async function getDashboard(req, res) {
    try {
        const { id } = req.params;

        // 1. Fetch Job safely (UUID vs ObjectId)
        const isObjectId = /^[0-9a-fA-F]{24}$/.test(id);
        const query = isObjectId
            ? { $or: [{ _id: id }, { job_id: id }] }
            : { job_id: id };

        const job = await Job.findOne(query);

        if (!job) {
            return res.status(404).json(
                errorResponse({ message: "Intelligence report not found" }, { trace_id: req.traceId })
            );
        }

        const userId = job.context?.user_id;
        const domain = job.context?.domain || "blackops";

        if (!userId) {
            return res.status(400).json(
                errorResponse({ message: "Job context is missing user_id" }, { trace_id: req.traceId })
            );
        }

        // 2. Fetch Profile & Patterns (Parallel)
        const [profile, patterns] = await Promise.all([
            PlayerProfile.findOne({ user_id: userId, domain }),
            PatternInsight.find({ user_id: userId, domain }).sort({ frequency: -1 }).limit(5)
        ]).catch(err => {
            console.error("Aggregation Fetch Error:", err);
            return [null, []];
        });

        // 3. Extract and Resolve Results (Phase 8 Robust Resolution)
        const steps = job.steps || [];
        const simulationStep = steps.find(s => s.name === "simulation" && s.status === "completed");
        const featureStep = steps.find(s => s.name === "feature_extraction" && s.status === "completed");

        let simulationResult = simulationStep?.output_ref || {};
        let features = null;

        // Resolve Simulation Ref
        if (typeof simulationResult === "string" && simulationResult.startsWith("ref_")) {
            const segment = await Segment.findOne({ ref: simulationResult, domain }).lean();
            if (segment && segment.data) {
                simulationResult = segment.data;
            } else {
                console.warn(`[Trace:${req.traceId}] Failed to resolve simulation segment: ${simulationResult}`);
                simulationResult = {}; // Fallback to empty object to prevent property access errors
            }
        }

        // Resolve Features Ref
        const featureRef = featureStep?.output_ref;
        if (featureRef) {
            if (typeof featureRef === "string" && featureRef.startsWith("ref_")) {
                const segment = await Segment.findOne({ ref: featureRef, domain }).lean();
                features = segment?.data?.features || segment?.data || null;
            } else if (typeof featureRef === "object") {
                features = featureRef.features || featureRef;
            }
        }

        // Ensure simulationResult is an object
        if (!simulationResult || typeof simulationResult !== "object") {
            simulationResult = {};
        }

        const responseData = {
            id: job.job_id,
            status: job.status,
            execution_mode: job.execution_mode || "FULL",

            // Result Data
            predicted_action: simulationResult.predicted_action || "UNKNOWN",
            confidence: simulationResult.confidence || 0,
            reasoning: Array.isArray(simulationResult.reasoning) ? simulationResult.reasoning : (simulationResult.reasoning ? [simulationResult.reasoning] : []),
            coaching_tip: simulationResult.coaching_tip || "No specific guidance generated for this sequence.",
            features,

            // Context Data
            profile: profile ? {
                preferred_style: profile.preferred_style,
                aggression_score: profile.aggression_score,
                adaptability_score: profile.adaptability_score,
                total_simulations: profile.total_simulations,
                last_simulation: profile.last_simulation_at
            } : null,

            // Pattern Data
            patterns: (patterns || []).map(p => ({
                id: p._id,
                type: p.type,
                description: p.description,
                frequency: p.frequency,
                severity: p.severity
            })),

            metadata: {
                trace_id: job.context?.trace_id,
                created_at: job.createdAt
            }
        };

        return res.json(successResponse(responseData, { trace_id: req.traceId }));
    } catch (err) {
        console.error("Dashboard Controller Crash:", err);
        return res.status(500).json(
            errorResponse({ message: "Dashboard aggregation failed", details: err.message }, { trace_id: req.traceId })
        );
    }
}

module.exports = {
    getDashboard
};
