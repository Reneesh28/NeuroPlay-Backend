const { GAME_DOMAIN_MAP } = require("./domain.constants");

const resolveDomain = (game_id) => {
    // 🔍 normalize input (important)
    const normalizedGameId = game_id?.toLowerCase();

    const domain = GAME_DOMAIN_MAP[normalizedGameId];

    if (!domain) {
        const error = new Error(`Invalid game_id: ${game_id}`);
        error.code = "INVALID_GAME_ID";
        error.statusCode = 400;
        throw error;
    }

    return domain;
};

module.exports = { resolveDomain };