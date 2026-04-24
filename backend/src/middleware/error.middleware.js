const { errorResponse } = require("../contracts/api.contract");

const errorMiddleware = (err, req, res, next) => {
    console.error("ERROR:", err);

    const statusCode = err.statusCode || 500;

    return res.status(statusCode).json(
        errorResponse(err, {
            trace: req.path
        })
    );
};

module.exports = { errorMiddleware };