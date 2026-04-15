const axios = require("axios");

const AI_URL = process.env.AI_SERVICE_URL;

async function execute(payload) {
    if (!AI_URL) {
        throw new Error("AI_SERVICE_URL not configured");
    }

    const response = await axios.post(AI_URL, payload);
    return response.data;
}

module.exports = {
    execute,
};