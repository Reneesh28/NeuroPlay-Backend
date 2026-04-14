const { createClient } = require("redis");
const env = require("./env");

const client = createClient({
    url: env.redisUrl,
});

client.on("error", (err) => {
    console.error("❌ Redis Error:", err);
});

client.connect();

console.log("✅ Redis Connected");

module.exports = client;