/**
 * Authentication Middleware
 * Validates JWT from Authorization header.
 */
const jwt = require('jsonwebtoken');
const { errorResponse } = require('../contracts/api.contract');

const JWT_SECRET = process.env.JWT_SECRET || 'neuroplay-core-secret-2026';

const authMiddleware = (req, res, next) => {
    // 1. Get token from header
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        // For development/demo, we might allow falling back to demo-user if not in production
        // But the goal is to enforce auth.
        if (process.env.NODE_ENV === 'development' && req.body.user_id === 'demo-user') {
            req.user = { id: 'demo-user', role: 'guest' };
            return next();
        }

        return res.status(401).json(
            errorResponse({ 
                message: "Authentication required",
                code: "AUTH_REQUIRED" 
            }, {
                trace_id: req.traceId
            })
        );
    }

    const token = authHeader.split(' ')[1];

    try {
        // 2. Verify token
        const decoded = jwt.verify(token, JWT_SECRET);
        
        // 3. Attach user to request
        req.user = decoded;
        
        // 🔥 Ensure req.validatedBody.user_id matches token user_id for security
        if (req.body && req.body.user_id && req.body.user_id !== decoded.id) {
            return res.status(403).json(
                errorResponse({ 
                    message: "User identity mismatch",
                    code: "IDENTITY_MISMATCH" 
                }, {
                    trace_id: req.traceId
                })
            );
        }

        next();
    } catch (err) {
        return res.status(401).json(
            errorResponse({ 
                message: "Invalid or expired token",
                code: "INVALID_TOKEN" 
            }, {
                trace_id: req.traceId
            })
        );
    }
};

module.exports = { authMiddleware };
