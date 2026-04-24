const successResponse = (data, meta = {}) => {
    return {
        success: true,
        data,
        error: null,
        meta
    };
};

const errorResponse = (error, meta = {}) => {
    return {
        success: false,
        data: null,
        error: {
            message: error.message || "Something went wrong",
            code: error.code || "INTERNAL_ERROR"
        },
        meta
    };
};

module.exports = {
    successResponse,
    errorResponse
};