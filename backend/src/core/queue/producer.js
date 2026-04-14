const { defaultQueue } = require("./queues");

class QueueProducer {
    async addJob(name, data) {
        const job = await defaultQueue.add(name, data);
        return job;
    }
}

module.exports = new QueueProducer();