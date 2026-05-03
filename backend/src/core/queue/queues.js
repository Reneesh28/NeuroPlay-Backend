const { Queue } = require("bullmq");
const connection = require("../../config/redis"); // 🔥 FIX

// 🔥 Step-Based Queues
const ingestionQueue = new Queue("ingestion-queue", { connection });
const processingQueue = new Queue("processing-queue", { connection });
const embeddingQueue = new Queue("embedding-queue", { connection });
const simulationQueue = new Queue("simulation-queue", { connection });

// 🔥 Dead Letter Queue
const deadLetterQueue = new Queue("dead-letter-queue", { connection });

module.exports = {
    ingestionQueue,
    processingQueue,
    embeddingQueue,
    simulationQueue,
    deadLetterQueue,
    defaultQueue: processingQueue
};