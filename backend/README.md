# NeuroPlay Backend API & Worker 🌐⚙️

The **Backend API** is the central orchestrator for the NeuroPlay ecosystem. Built with **Node.js** and **Express**, it exposes RESTful endpoints for client interaction, handles file uploads, and manages asynchronous tasks via a robust **BullMQ** job queue.

---

## 🏗️ Architecture

The backend is split into two primary operational modes:

1. **Express API Server (`server.js`)**: Handles synchronous client requests (e.g., job creation, status polling, file uploads). It pushes compute-heavy tasks to the job queue to avoid blocking the event loop.
2. **BullMQ Worker Process (`worker.js`)**: A background process that consumes jobs from the Redis queue. It acts as the driver for the 5-step ML pipeline, making HTTP calls to the `ai-engine` microservice and aggregating the results in MongoDB.

---

## 🚦 The Job Pipeline

When a simulation job is created, the worker processes it through the following states in sequential order:

1. `video_processing`
2. `feature_extraction`
3. `embedding_generation`
4. `clustering`
5. `simulation`

Between each step, the worker records the state in **MongoDB** (`Job` collection) and updates the job's progress in **BullMQ**. If a step fails, the worker can safely retry without restarting the entire pipeline.

---

## 🚀 Getting Started

### Prerequisites
- Node.js v18+
- MongoDB (Local or Atlas)
- Redis Server (Must be running for BullMQ)

### Installation & Setup

1. **Navigate to the directory**:
   ```bash
   cd core-backend/backend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Environment Variables**:
   Create a `.env` file in the root of the `backend` directory:
   ```env
   PORT=5000
   MONGO_URI=mongodb://127.0.0.1:27017/neuroplay
   REDIS_HOST=127.0.0.1
   REDIS_PORT=6379
   ```

### Running the Services

> **⚠️ CRITICAL**: For the system to process jobs, you **MUST** run both the API server and the Worker process simultaneously.

**Terminal 1 (Start the API Server):**
```bash
npm run dev
# Server will start on http://localhost:5000
```

**Terminal 2 (Start the Job Worker):**
```bash
node worker.js
# Worker will connect to Redis and wait for jobs
```

---

## 🔗 Key API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/job` | Creates a new pipeline job and enqueues it. |
| `GET`  | `/api/job/:id` | Polls the real-time status and output of a job. |
| `POST` | `/api/upload` | Uploads a file (using Multer) to be processed. |

---

## 🐛 Common Troubleshooting

- **Worker fails with `Operation buffering timed out`**: The worker was started before MongoDB was fully connected. Check your `MONGO_URI`.
- **`maxRetriesPerRequest must be null`**: This is a strict BullMQ requirement. Ensure that the Redis instance passed to the Worker/Queue does not have retry limits set. This is properly handled in `src/config/redis.js`.
- **Jobs are stuck in `waiting`**: Ensure your Redis server is running and the `node worker.js` process is active.
