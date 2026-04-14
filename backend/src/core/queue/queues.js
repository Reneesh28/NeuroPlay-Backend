const { Queue } = require("bullmq");
const queueConfig = require("./queue.config");

// Default queue (we expand later)
const defaultQueue = new Queue("default-queue", queueConfig);

module.exports = {
    defaultQueue,
};