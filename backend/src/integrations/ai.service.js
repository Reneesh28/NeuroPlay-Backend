const axios = require("axios");

const AI_BASE_URL = "http://localhost:8000";

class AIService {
    async executeStep({ jobId, step, inputData = {} }) {
        try {
            const response = await axios.post(`${AI_BASE_URL}/ai/execute`, {
                job_id: jobId,
                step,
                input_data: inputData,
            });

            return response.data;
        } catch (error) {
            console.error("❌ AI Service Error:", error.message);
            throw error;
        }
    }
}

module.exports = new AIService();