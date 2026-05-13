const { rateLimit } = require('express-rate-limit');
const { RedisStore } = require('rate-limit-redis');
const redisClient = require('../config/redis');
const { errorResponse } = require('../contracts/api.contract');

// 🔒 Helper to create unique Redis stores
const createStore = (prefix) => new RedisStore({
    // @ts-ignore
    sendCommand: (...args) => redisClient.call(...args),
    prefix: `rl:${prefix}:`,
});

// 🟢 Standard API (High Velocity: 1000 req / 15 min)
const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 1000,
    standardHeaders: true,
    legacyHeaders: false,
    store: createStore('api'),
    handler: (req, res) => {
        res.status(429).json(
            errorResponse({
                message: "Too many requests. Neural processing capacity reached.",
                code: "RATE_LIMIT_EXCEEDED"
            }, { trace_id: req.traceId })
        );
    }
});

// 🔴 Auth Security (Moderate: 50 attempts / 15 min)
const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 50,
    standardHeaders: true,
    legacyHeaders: false,
    store: createStore('auth'),
    handler: (req, res) => {
        res.status(429).json(
            errorResponse({
                message: "Security block: Too many auth attempts. Please wait 15 minutes.",
                code: "RATE_LIMIT_EXCEEDED"
            }, { trace_id: req.traceId })
        );
    }
});

// 🧠 AI Simulation (High Capacity: 100 per hour)
const simulationLimiter = rateLimit({
    windowMs: 60 * 60 * 1000,
    max: 100,
    standardHeaders: true,
    legacyHeaders: false,
    store: createStore('simulation'),
    handler: (req, res) => {
        res.status(429).json(
            errorResponse({
                message: "Simulation quota exceeded. Cooling down neural engines.",
                code: "RATE_LIMIT_EXCEEDED"
            }, { trace_id: req.traceId })
        );
    }
});

// 📁 Data Ingestion (High Ingestion: 5000 chunks per hour)
const uploadLimiter = rateLimit({
    windowMs: 60 * 60 * 1000,
    max: 5000,
    standardHeaders: true,
    legacyHeaders: false,
    store: createStore('upload'),
    handler: (req, res) => {
        res.status(429).json(
            errorResponse({
                message: "Upload quota exceeded. Reducing ingestion velocity.",
                code: "RATE_LIMIT_EXCEEDED"
            }, { trace_id: req.traceId })
        );
    }
});

module.exports = {
    apiLimiter,
    authLimiter,
    simulationLimiter,
    uploadLimiter
};
