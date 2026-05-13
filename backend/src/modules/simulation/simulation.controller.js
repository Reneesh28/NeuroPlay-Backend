const jobService = require("../../core/jobs/job.service");
const producer = require("../../core/queue/producer");
const { buildContext } = require("../../core/jobs/context.builder");
const Job = require("../../core/jobs/job.model");
const { successResponse } = require("../../contracts/api.contract");
const { resolveDomain } = require("../../core/domain/domain.resolver");

exports.runSimulation = async (req, res, next) => {
    try {
        const { user_id, game_id, domain: requestedDomain, payload } = req.validatedBody;
        const { scenario } = payload || {};

        // Resolve domain if not explicitly provided
        const domain = requestedDomain || resolveDomain(game_id);

        const context = buildContext({
            user_id,
            session_id: req.validatedBody.session_id || "demo-session",
            game_id,
            domain,
            trace_id: req.traceId
        });

        const job = await jobService.createJob({
            context,
            input_ref: { scenario }
        });

        // Push to queue
        await producer.enqueueJobStep(job, job.current_step, { scenario });

        return res.json(
            successResponse({
                job_id: job.job_id
            }, {
                trace_id: req.headers['x-trace-id']
            })
        );
    } catch (err) {
        next(err);
    }
};
