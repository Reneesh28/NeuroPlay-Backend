const { v4: uuidv4 } = require("uuid");

// 🔥 Build execution context (IMMUTABLE)
const buildContext = ({ user_id, session_id, game_id, domain }) => {
    return {
        user_id,
        session_id: session_id || null,

        game_id,
        domain,

        // 🔥 versioning (future-proof)
        versions: {
            model: "v1",
            feature: "v1",
            pipeline: "v1"
        },

        // 🔥 tracing
        trace_id: uuidv4()
    };
};

module.exports = { buildContext };