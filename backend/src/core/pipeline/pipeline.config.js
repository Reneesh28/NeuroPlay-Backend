const { PIPELINE_STEPS } = require("./step.constants");

// 🔥 Ordered deterministic execution
const PIPELINE_ORDER = [...PIPELINE_STEPS];

module.exports = {
    PIPELINE_ORDER
};