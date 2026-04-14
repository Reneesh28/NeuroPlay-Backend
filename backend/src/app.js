const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

// Health check route
app.get("/health", (req, res) => {
    res.json({
        status: "ok",
        service: "backend",
    });
});

module.exports = app;