const { GAME_DOMAIN_MAP } = require("./domain.constants");

/**
 * 🔍 Domain Resolver
 * 
 * Maps specific Game IDs (bo6, mw3, wz) to high-level Tactical Domains.
 * Self-healing: If the input is already a valid domain, it passes through.
 */
const resolveDomain = (game_id) => {
    if (!game_id) return "blackops";

    const normalizedInput = game_id.toLowerCase();

    // 1. Check if it's a known Game ID
    let domain = GAME_DOMAIN_MAP[normalizedInput];

    // 2. Self-healing: Check if it's already a valid Domain name
    const validDomains = ["blackops", "warzone", "modern_warfare"];
    if (!domain && validDomains.includes(normalizedInput)) {
        domain = normalizedInput;
    }

    if (!domain) {
        const error = new Error(`Invalid game_id: ${game_id}`);
        error.code = "INVALID_GAME_ID";
        error.statusCode = 400;
        throw error;
    }

    return domain;
};

module.exports = { resolveDomain };