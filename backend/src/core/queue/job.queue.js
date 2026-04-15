const { Queue } = require("bullmq");
const connection = require("../../config/redis");

const jobQueue = new Queue("jobQueue", {
    connection,
});

module.exports = jobQueue;