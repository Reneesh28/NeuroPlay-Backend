/**
 * Trace Middleware
 * Captures 'x-trace-id' from headers or generates a new one.
 * Attaches it to req object for propagation.
 */
const { v4: uuidv4 } = require('uuid');

const traceMiddleware = (req, res, next) => {
    let traceId = req.headers['x-trace-id'];
    
    if (!traceId) {
        traceId = uuidv4();
    }
    
    // Attach to request for controllers to use
    req.traceId = traceId;
    
    // Set response header for debugging
    res.setHeader('x-trace-id', traceId);
    
    next();
};

module.exports = { traceMiddleware };
