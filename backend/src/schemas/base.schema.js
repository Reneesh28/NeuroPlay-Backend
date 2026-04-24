const { z } = require("zod");

const baseRequestSchema = z.object({
    user_id: z.string({
        required_error: "user_id is required"
    }),

    session_id: z.string().optional(),

    game_id: z.string({
        required_error: "game_id is required"
    }),

    payload: z.any()
});

module.exports = { baseRequestSchema };