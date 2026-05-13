const { z } = require("zod");

/**
 * 📦 BASE REQUEST SCHEMA
 * Standardized validation for all incoming API requests.
 */
const baseRequestSchema = z.object({
    user_id: z.string({
        required_error: "user_id is required"
    }),
    game_id: z.string({
        required_error: "game_id is required"
    }),
    domain: z.string().optional(),
    session_id: z.string().optional(),
    // Using a more stable any() for payload to avoid record-type issues in experimental Zod versions
    payload: z.any().optional()
});

module.exports = { baseRequestSchema };