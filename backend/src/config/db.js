const mongoose = require("mongoose");
const env = require("./env");

const connectDB = async () => {
    try {
        await mongoose.connect(env.mongoUri);
        console.log("✅ MongoDB Connected");
    } catch (error) {
        console.error("❌ MongoDB Error:", error);
        process.exit(1);
    }
};

module.exports = connectDB;