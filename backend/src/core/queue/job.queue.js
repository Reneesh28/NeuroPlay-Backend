const { Queue } = require("bullmq");
const connection = require("../../config/redis");

const jobQueue = new Queue("processJob", {
    connection,
});

module.exports = jobQueue;