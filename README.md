# NeuroPlay Core Backend 🧠🎮

The high-performance, multi-service backend infrastructure for the NeuroPlay ecosystem.
This repository houses the central Express API gateway, an asynchronous BullMQ job pipeline, an AI processing engine (Python/FastAPI), and all supporting infrastructure.

---

## 🏗️ Architecture Overview

NeuroPlay Core Backend is built around a **Queue-Driven Workflow Engine** designed for handling complex, long-running AI tasks without blocking the primary API.

```
Client Request
      │
      ▼
 Express API  ──── enqueues ────▶  BullMQ (Redis) ──── consumed by ────▶  Worker Process
      │                                                                          │
      │                                                                          ▼
      │                                                               5-Step AI Pipeline
      │                                                               (via AI Engine)
      ▼
  Job Status / Results
```

### Core Services

| Service | Runtime | Responsibility |
| :--- | :--- | :--- |
| **Backend API** | Node.js / Express | Job creation, status polling, file uploads |
| **Job Worker** | Node.js / BullMQ | Consumes queue jobs, drives the 5-step pipeline |
| **AI Engine** | Python / FastAPI | Executes individual AI processing steps |

---

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| API Framework | [Express v5](https://expressjs.com/) (Node.js) |
| AI Service | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.9+) |
| Job Queue | [BullMQ](https://docs.bullmq.io/) |
| Queue Broker | [Redis](https://redis.io/) via `ioredis` |
| Database | [MongoDB](https://www.mongodb.com/) via Mongoose |
| File Uploads | [Multer](https://github.com/expressjs/multer) |
| Inter-service | [Axios](https://axios-http.com/) |
| Dev Server | Nodemon |

---

## 🚦 5-Step Processing Pipeline

Every simulation job is processed through a sequential, stateful pipeline. Each step is executed by the AI Engine and its result is persisted to MongoDB before the next step starts.

| Step | Name | Description |
| :---: | :--- | :--- |
| 1 | `video_processing` | AI-driven ingestion and analysis of raw video inputs |
| 2 | `feature_extraction` | Extracting meaningful data points from processed video |
| 3 | `embedding_generation` | Converting features into multi-dimensional vectors |
| 4 | `clustering` | Grouping related features and behavioral patterns |
| 5 | `simulation` | Final simulation computation from aggregated data |

On completion, results are aggregated by `result.aggregator.js` and stored in `job.output_ref`.

---

## 🔗 API Endpoints

### 🟢 Backend API (Node.js · `PORT=5000`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health check |
| `GET` | `/api` | API discovery root |
| `POST` | `/api/upload` | Upload a file for processing (multipart/form-data) |
| `POST` | `/api/job` | Create a new simulation pipeline job |
| `GET` | `/api/job/:id` | Retrieve status, progress & results of a job |
| `POST` | `/api/test/process/:jobId` | Directly trigger processing for a job ID (dev/testing) |

### 🔵 AI Engine (Python · `PORT=8000`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health check |
| `POST` | `/ai/execute` | Execute a specific AI pipeline step for a given job |

---

## 🚀 Getting Started

### 1. Prerequisites

- **Node.js** v18+
- **Python** 3.9+
- **MongoDB** running (local or Atlas)
- **Redis** server running (local or Docker)

### 2. Environment Configuration

**Backend (`/backend/.env`):**
```env
PORT=5000
MONGO_URI=mongodb://127.0.0.1:27017/neuroplay
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

**AI Engine (`/ai-engine/.env`):**
```env
PORT=8000
```

### 3. Run the Backend

```bash
# Navigate to the backend service
cd core-backend/backend

# Install dependencies
npm install

# Start the API server (with hot-reload)
npm run dev

# In a separate terminal — start the background worker
node worker.js
```

> ⚠️ The API server and the worker process are **separate processes** and must both be running for end-to-end job execution to work.

### 4. Run the AI Engine

```bash
# Navigate to the AI engine service
cd core-backend/ai-engine

# Create and activate the virtual environment
python -m venv venv
venv/Scripts/activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI service
uvicorn app.main:app --reload --port 8000
```

---

## 📁 Directory Structure

```text
core-backend/
├── .gitignore
├── README.md
│
├── backend/                        # Node.js / Express Service
│   ├── server.js                   # HTTP server entry point
│   ├── worker.js                   # BullMQ worker entry point (run separately)
│   ├── package.json
│   └── src/
│       ├── app.js                  # Express app setup & route registration
│       ├── config/
│       │   └── redis.js            # ioredis connection (maxRetriesPerRequest: null)
│       ├── core/
│       │   ├── config/             # Shared core configs
│       │   ├── database/           # Mongoose connection
│       │   ├── jobs/
│       │   │   ├── job.model.js    # Mongoose Job schema
│       │   │   └── job.service.js  # Job CRUD helpers
│       │   ├── middleware/         # Error handling middleware
│       │   ├── pipeline/
│       │   │   ├── step.constants.js
│       │   │   ├── step.registry.js
│       │   │   ├── pipeline.config.js
│       │   │   ├── input.processor.js
│       │   │   ├── output.formatter.js
│       │   │   └── result.aggregator.js
│       │   ├── queue/
│       │   │   ├── job.queue.js    # BullMQ Queue definition
│       │   │   ├── job.worker.js   # BullMQ Worker definition
│       │   │   ├── producer.js     # Job enqueue helper
│       │   │   ├── queue.config.js
│       │   │   └── queues.js
│       │   └── workers/
│       │       ├── worker.js       # processJob() — drives the 5-step loop
│       │       └── processors/     # One file per pipeline step
│       │           ├── ingestion.processor.js
│       │           ├── feature.processor.js
│       │           ├── embedding.processor.js
│       │           ├── clustering.processor.js
│       │           └── simulation.processor.js
│       ├── integrations/           # Axios clients for AI Engine
│       ├── modules/
│       │   ├── index.js            # Module router
│       │   ├── job/                # Job status API (routes + controller)
│       │   ├── upload/             # Multer file upload (routes + controller + service)
│       │   ├── coach/              # Coaching module
│       │   ├── dashboard/          # Dashboard module
│       │   ├── profile/            # User profile module
│       │   └── simulation/         # Simulation module
│       └── utils/                  # Shared utility functions
│
├── ai-engine/                      # Python / FastAPI Service
│   ├── .env
│   └── app/
│       ├── main.py                 # FastAPI app entry
│       ├── api/                    # Route definitions
│       ├── core/                   # Config / settings
│       ├── processors/             # AI step logic (Python)
│       └── schemas/                # Pydantic models
│
├── infrastructure/                 # Deployment configs (Docker, CI/CD)
├── shared/                         # Common schemas across services
├── scripts/                        # Utility scripts
└── tests/                          # Integration / E2E tests
```

---

## 🐛 Troubleshooting

### `BullMQ: maxRetriesPerRequest must be null`
BullMQ requires the Redis connection used for workers to have `maxRetriesPerRequest: null`. This is already set in `src/config/redis.js`. If you are creating additional Redis connections elsewhere, ensure the same option is applied.

### Worker fails with `Operation buffering timed out`
This means the worker process started before MongoDB established a connection. Ensure `MONGO_URI` in `.env` is correct and MongoDB is reachable before starting the worker. The database connection is initialized lazily on the first model call.

### Port conflicts
Ensure nothing else is running on port `5000` (API) or `8000` (AI Engine). Change the `PORT` variable in the respective `.env` files if needed.

---

## 📝 License

This project is licensed under the **ISC License**.
