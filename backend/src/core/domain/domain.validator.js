const { GAME_DOMAIN_MAP } = require("./domain.constants");

// 🔥 Check if domain is valid
const isValidDomain = (domain) => {
    return Object.values(GAME_DOMAIN_MAP).includes(domain);
};

// 🔥 Enforce domain consistency (future use in jobs/pipeline)
const assertDomainConsistency = (expectedDomain, actualDomain) => {
    if (expectedDomain !== actualDomain) {
        const error = new Error(
            `Domain mismatch: expected ${expectedDomain}, got ${actualDomain}`
        );
        error.code = "DOMAIN_MISMATCH";
        error.statusCode = 400;
        throw error;
    }
};

// 🔥 Validate domain existence
const assertValidDomain = (domain) => {
    if (!isValidDomain(domain)) {
        const error = new Error(`Invalid domain: ${domain}`);
        error.code = "INVALID_DOMAIN";
        error.statusCode = 400;
        throw error;
    }
};

module.exports = {
    isValidDomain,
    assertDomainConsistency,
    assertValidDomain
};