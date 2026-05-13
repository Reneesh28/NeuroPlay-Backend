/**
 * Middleware to move top-level multipart fields into the 'payload' object
 * so they pass through baseRequestSchema validation.
 */
const prepareMultipartPayload = (fields = []) => (req, res, next) => {
    if (!req.body) req.body = {};
    if (!req.body.payload) req.body.payload = {};

    // If payload is a string (e.g. sent as JSON in FormData), parse it
    if (typeof req.body.payload === 'string') {
        try {
            req.body.payload = JSON.parse(req.body.payload);
        } catch (e) {
            // Keep as is if not JSON
        }
    }

    fields.forEach(field => {
        if (req.body[field] !== undefined && req.body.payload[field] === undefined) {
            req.body.payload[field] = req.body[field];
            // We can optionally delete req.body[field] here, 
            // but validation will strip it anyway.
        }
    });

    next();
};

module.exports = { prepareMultipartPayload };
