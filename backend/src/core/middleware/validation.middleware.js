const validate = (schema) => (req, res, next) => {
    if (!schema) return next();

    const result = schema.safeParse({
        body: req.body,
        query: req.query,
        params: req.params,
    });

    if (!result.success) {
        return res.status(400).json({
            success: false,
            error: {
                message: "Validation failed",
                details: result.error.errors,
            },
        });
    }

    next();
};

module.exports = validate;