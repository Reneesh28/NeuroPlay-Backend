const Job = require("./job.model");

class JobService {
    async createJob({ user_id, session_id, steps }) {
        const job = await Job.create({
            user_id,
            session_id,
            steps,
            status: "queued",
        });

        return job;
    }

    async updateJobStatus(jobId, status) {
        return Job.findByIdAndUpdate(
            jobId,
            { status, updated_at: new Date() },
            { returnDocument: "after" }
        );
    }

    async updateStep(jobId, stepName, updates) {
        const job = await Job.findById(jobId);

        if (!job) throw new Error("Job not found");

        const step = job.steps.find((s) => s.name === stepName);

        if (!step) throw new Error("Step not found");

        Object.assign(step, updates);

        job.updated_at = new Date();

        await job.save();

        return job;
    }

    async getJob(jobId) {
        return Job.findById(jobId);
    }
}

module.exports = new JobService();