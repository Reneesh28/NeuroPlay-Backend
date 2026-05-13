const Job = require("../../core/jobs/job.model");
const { successResponse, errorResponse } = require("../../contracts/api.contract");
const { deadLetterQueue } = require("../../core/queue/queues");
const producer = require("../../core/queue/producer");

// 🔥 Progress Calculator
function calculateProgress(steps) {
    if (!steps || steps.length === 0) return 0;

    const total = steps.length;
    const completed = steps.filter(s => s.status === "completed").length;

    return Math.round((completed / total) * 100);
}

// 🔥 GET JOB DETAILS
async function getJob(req, res) {
    try {
        const { id } = req.params;
        // Search by both _id and job_id for flexibility
        let job = await Job.findById(id).catch(() => null);
        if (!job) job = await Job.findOne({ job_id: id });

        if (!job) {
            return res.status(404).json(
                errorResponse({ message: "Job not found" }, { trace_id: req.traceId })
            );
        }

        const progress = calculateProgress(job.steps);

        return res.json(
            successResponse({
                id: job._id,
                job_id: job.job_id,
                status: job.status,
                current_step: job.current_step,
                progress,
                context: job.context,
                steps: job.steps,
                created_at: job.created_at,
                updated_at: job.updated_at,
            }, {
                trace_id: req.traceId
            })
        );
    } catch (error) {
        return res.status(500).json(
            errorResponse(error, { trace_id: req.traceId })
        );
    }
}

// 🔥 LIST DLQ JOBS
async function listDLQ(req, res) {
    try {
        const jobs = await deadLetterQueue.getJobs(["waiting", "active", "completed", "failed", "delayed"]);
        
        return res.json(
            successResponse(jobs.map(j => ({
                id: j.id,
                data: j.data,
                timestamp: j.timestamp
            })), {
                trace_id: req.traceId
            })
        );
    } catch (error) {
        return res.status(500).json(
            errorResponse(error, { trace_id: req.traceId })
        );
    }
}

// 🔥 REPLAY JOB
async function replayJob(req, res) {
    try {
        const { jobId } = req.params;
        const bullJob = await deadLetterQueue.getJob(jobId);

        if (!bullJob) {
            return res.status(404).json(
                errorResponse({ message: "DLQ Job not found" }, { trace_id: req.traceId })
            );
        }

        const { job_id, step, input_ref } = bullJob.data;
        const dbJob = await Job.findOne({ job_id });

        if (!dbJob) {
            throw new Error("Associated DB Job not found");
        }

        // Reset step status
        const stepIndex = dbJob.steps.findIndex(s => s.name === step);
        if (stepIndex !== -1) {
            dbJob.steps[stepIndex].status = "pending";
            dbJob.status = "processing";
            dbJob.current_step = step;
            await dbJob.save();
        }

        // Re-enqueue
        await producer.enqueueJobStep(dbJob, step, input_ref);

        // Remove from DLQ
        await bullJob.remove();

        return res.json(
            successResponse({ message: "Job replayed successfully" }, { trace_id: req.traceId })
        );
    } catch (error) {
        return res.status(500).json(
            errorResponse(error, { trace_id: req.traceId })
        );
    }
}

// 🔥 CANCEL JOB
async function cancelJob(req, res) {
    try {
        const { id } = req.params;
        const job = await Job.findById(id);

        if (!job) {
            return res.status(404).json(
                errorResponse({ message: "Job not found" }, { trace_id: req.traceId })
            );
        }

        if (job.status === "completed" || job.status === "failed") {
            return res.status(400).json(
                errorResponse({ message: "Cannot cancel a finished job" }, { trace_id: req.traceId })
            );
        }

        job.status = "failed";
        job.error = { message: "Job cancelled by user", type: "USER_CANCEL" };
        await job.save();

        return res.json(
            successResponse({ message: "Job cancellation initiated" }, { trace_id: req.traceId })
        );
    } catch (error) {
        return res.status(500).json(
            errorResponse(error, { trace_id: req.traceId })
        );
    }
}

// 🔥 GET USER JOBS
async function getUserJobs(req, res) {
    try {
        const userId = req.user?.id; // Assuming authMiddleware attaches req.user
        
        if (!userId) {
            return res.status(401).json(
                errorResponse({ message: "Unauthorized: User context missing" }, { trace_id: req.traceId })
            );
        }

        const jobs = await Job.find({ "context.user_id": userId })
            .sort({ "created_at": -1 })
            .limit(20)
            .lean(); // Faster query, returns plain JS objects

        // Enhance jobs with progress if needed
        const enhancedJobs = jobs.map(job => ({
            id: job._id,
            job_id: job.job_id,
            status: job.status,
            current_step: job.current_step,
            progress: calculateProgress(job.steps),
            created_at: job.created_at
        }));

        return res.json(
            successResponse(enhancedJobs, { trace_id: req.traceId })
        );

    } catch (error) {
        console.error("getUserJobs Error:", error);
        return res.status(500).json(
            errorResponse({ message: "Failed to fetch user jobs", details: error.message }, { trace_id: req.traceId })
        );
    }
}

module.exports = {
    getJob,
    getUserJobs,
    listDLQ,
    replayJob,
    cancelJob
};