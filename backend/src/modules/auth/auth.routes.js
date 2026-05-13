const express = require('express');
const router = express.Router();
const controller = require('./auth.controller');
const { authLimiter } = require('../../middleware/limiter.middleware');
const { authMiddleware } = require('../../middleware/auth.middleware');

/**
 * 🔐 AUTHENTICATION ENDPOINTS
 * Rate limited for security.
 */

router.post('/register', authLimiter, controller.register);
router.post('/login', authLimiter, controller.login);

// 🛡️ Protected route to get current operator context
router.get('/me', authMiddleware, controller.me);
module.exports = router;