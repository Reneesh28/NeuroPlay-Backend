const validate = (schema) => (req, res, next) => {
    try {
        const parsed = schema.parse(req.body);

        // attach validated data
        req.validatedBody = parsed;

        next();
    } catch (err) {
        return res.status(400).json({
            success: false,
            data: null,
            error: {
                message: err.errors?.[0]?.message || "Validation failed",
                code: "VALIDATION_ERROR"
            },
            meta: {}
        });
    }
};

module.exports = { validate };