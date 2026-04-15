function aggregateResults(job) {
    const result = {
        summary: "Pipeline execution completed",
        steps: {},
    };

    for (const step of job.steps) {
        result.steps[step.name] = {
            status: step.status || "unknown",

            // 🔥 Ensure clean output
            output: step.output ?? null,

            // 🔥 Avoid empty {} → convert to null
            error: step.error && Object.keys(step.error).length > 0
                ? step.error
                : null,

            // 🔥 Optional but VERY useful (keep it)
            meta: step.meta || null,
        };
    }

    return result;
}

module.exports = {
    aggregateResults,
};