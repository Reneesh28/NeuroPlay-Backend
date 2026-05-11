const jobService = require("../../core/jobs/job.service");
const producer = require("../../core/queue/producer");
const { buildContext } = require("../../core/jobs/context.builder");
const Job = require("../../core/jobs/job.model");

exports.runSimulation = async (req, res, next) => {
    try {
        const { scenario, domain } = req.body;

        const context = buildContext({
            user_id: req.user?.id || "demo-user",
            session_id: "demo-session",
            game_id: "demo-game",
            domain: domain || "blackops"
        });

        const job = await jobService.createJob({
            context,
            input_ref: { scenario }
        });

        // Artificially skip to simulation if needed, or let the pipeline handle it.
        // For Phase 8 we'll assume the pipeline handles text inputs in simulation if they pass through,
        // or we manually set it to simulation for quick testing.
        
        // Push to queue
        await producer.enqueueJobStep(job, job.current_step);

        res.json({
            success: true,
            data: {
                job_id: job._id
            }
        });
    } catch (err) {
        next(err);
    }
};
