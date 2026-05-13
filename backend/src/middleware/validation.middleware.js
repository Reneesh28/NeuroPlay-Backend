const validate = (schema) => (req, res, next) => {
    console.log("📦 [INCOMING_BODY]:", req.body);
    try {
        const parsed = schema.parse(req.body);

        // attach validated data
        req.validatedBody = parsed;

        next();
    } catch (err) {
        console.log("❌ [VALIDATION_ERROR]:", JSON.stringify(err.errors || err.issues || err, null, 2));
        return res.status(400).json({
            success: false,
            data: null,
            error: {
                message: err.errors?.[0]?.message || err.message || "Validation failed",
                code: "VALIDATION_ERROR"
            },
            meta: {}
        });
    }
};

module.exports = { validate };