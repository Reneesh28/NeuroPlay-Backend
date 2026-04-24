const { Queue } = require("bullmq");
const queueConfig = require("./queue.config");

// 🔥 Step-Based Queues
const ingestionQueue = new Queue("ingestion-queue", queueConfig);
const processingQueue = new Queue("processing-queue", queueConfig);
const embeddingQueue = new Queue("embedding-queue", queueConfig);
const simulationQueue = new Queue("simulation-queue", queueConfig);

// 🔥 Dead Letter Queue (DLQ)
const deadLetterQueue = new Queue("dead-letter-queue", queueConfig);

module.exports = {
    ingestionQueue,
    processingQueue,
    embeddingQueue,
    simulationQueue,
    deadLetterQueue,
    defaultQueue: processingQueue // Fallback
};