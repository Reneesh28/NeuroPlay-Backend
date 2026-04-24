const axios = require("axios");

const AI_URL = process.env.AI_SERVICE_URL;

async function execute(payload) {
    if (!AI_URL) {
        throw new Error("AI_SERVICE_URL not configured");
    }

    const { job_id, step, context } = payload;
    console.log(`📡 Calling AI Engine [${step}] | Job: ${job_id} | Trace: ${context?.trace_id}`);

    const response = await axios.post(AI_URL, payload);
    return response.data;
}


module.exports = {
    execute,
};