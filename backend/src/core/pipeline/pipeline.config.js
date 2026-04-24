const { PIPELINE_STEPS } = require("./step.constants");

// 🔥 Ordered execution
const PIPELINE_ORDER = [...PIPELINE_STEPS];

module.exports = {
    PIPELINE_ORDER
};