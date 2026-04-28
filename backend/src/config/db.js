const mongoose = require("mongoose");
const env = require("./env");

const connectDB = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URI, {
            dbName: process.env.DB_NAME,
            maxPoolSize: 20,
        });

        console.log(`✅ Mongo Connected: ${process.env.DB_NAME}`);
    } catch (err) {
        console.error("❌ DB Error:", err);
        process.exit(1);
    }
};

module.exports = connectDB;