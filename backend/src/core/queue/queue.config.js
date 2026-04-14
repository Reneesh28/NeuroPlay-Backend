const env = require("../../config/env");

module.exports = {
    connection: {
        url: env.redisUrl,
    },
};