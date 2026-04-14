const app = require("./src/app");
const connectDB = require("./src/config/db");
require("./src/config/redis");
const env = require("./src/config/env");

const PORT = env.port || 5000;

// Connect DB
connectDB();

app.listen(PORT, () => {
    console.log(`🚀 Backend running on port ${PORT}`);
});