require("dotenv").config();

const requiredEnv = [
    "PORT",
    "MONGO_URI",
    "REDIS_URL",
];

requiredEnv.forEach((key) => {
    if (!process.env[key]) {
        throw new Error(`❌ Missing environment variable: ${key}`);
    }
});

const env = {
    port: process.env.PORT,
    mongoUri: process.env.MONGO_URI,
    redisUrl: process.env.REDIS_URL,
};

module.exports = env;