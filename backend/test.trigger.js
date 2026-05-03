require("dotenv").config(); // 🔥 REQUIRED

const mongoose = require("mongoose");
const producer = require("./src/core/queue/producer");
const Job = require("./src/core/jobs/job.model");

const MONGO_URI = process.env.MONGO_URI;

async function trigger() {
    if (!MONGO_URI) {
        throw new Error("❌ MONGO_URI missing in .env");
    }

    await mongoose.connect(MONGO_URI);
    console.log("✅ Mongo Connected (trigger)");

    const job_id = "job_pipeline_1";

    const context = {
        user_id: "user1",
        session_id: "session1",
        domain: "blackops",
        game_id: "bo1",
        trace_id: "trace_pipeline",

        // 🔥 REQUIRED — FLAT VERSION FIELDS
        feature_version: "v1",
        pipeline_version: "v1",
        resolved_model_version: "v1"
    };

    const jobData = {
        job_id,
        current_step: "embedding_generation",
        status: "queued",
        execution_mode: "FULL",

        // 🔥 REQUIRED FOR STEP TRACKING
        steps: [
            { name: "video_processing", status: "pending" },
            { name: "feature_extraction", status: "pending" },
            { name: "embedding_generation", status: "pending" },
            { name: "memory_retrieval", status: "pending" },
            { name: "simulation", status: "pending" }
        ],

        input_ref: null,
        output_ref: null,

        context
    };

    // 🔥 STEP 1 — INSERT JOB
    await Job.findOneAndUpdate(
        { job_id },
        jobData,
        {
            upsert: true,
            returnDocument: "after"
        }
    );

    console.log("🧾 Job inserted in DB");

    // 🔥 STEP 2 — ENQUEUE
    await producer.enqueueJobStep(
        { job_id, context },
        "embedding_generation",
        "test_inline_1"
    );

    console.log("🚀 Job queued");
}

trigger();