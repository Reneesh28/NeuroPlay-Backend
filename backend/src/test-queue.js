const producer = require("./core/queue/producer");

(async () => {
    const job = await producer.addJob("test-job", {
        message: "Hello Queue",
    });

    console.log("✅ Job added:", job.id);
})();