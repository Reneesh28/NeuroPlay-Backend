const IORedis = require("ioredis");

const connection = new IORedis({
    host: process.env.REDIS_HOST || "127.0.0.1",
    port: process.env.REDIS_PORT || 6379,

    // 🔥 CRITICAL FOR BULLMQ
    maxRetriesPerRequest: null,
});

connection.on("connect", () => {
    console.log("✅ Redis Connected");
});

connection.on("error", (err) => {
    console.error("❌ Redis Error:", err);
});

module.exports = connection;