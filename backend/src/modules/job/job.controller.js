const Job = require("../../core/jobs/job.model");

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

        const job = await Job.findById(id);

        if (!job) {
            return res.status(404).json({
                success: false,
                error: {
                    message: "Job not found"
                }
            });
        }

        const progress = calculateProgress(job.steps);

        return res.json({
            success: true,
            data: {
                id: job._id,
                status: job.status,
                current_step: job.current_step,
                progress,

                input: job.input_ref,
                output: job.output_ref,

                steps: job.steps.map(step => ({
                    name: step.name,
                    status: step.status,
                })),

                created_at: job.created_at,
                updated_at: job.updated_at,
            }
        });

    } catch (error) {
        return res.status(500).json({
            success: false,
            error: {
                message: error.message
            }
        });
    }
}

module.exports = {
    getJob,
};