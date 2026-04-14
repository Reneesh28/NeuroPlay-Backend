# NeuroPlay Core Backend 🧠🎮

The high-performance, multi-service backend infrastructure for the NeuroPlay ecosystem. This repository houses the central API gateways, asynchronous job pipelines, and the AI processing engine.

## 🏗️ Architecture Overview

NeuroPlay Core Backend utilizes a **Queue-Driven Workflow Engine** designed for handling complex, long-running AI tasks without blocking the main API response.

- **Central API (Node.js)**: Built with Express, serving as the interface for job creation, status monitoring, and client-facing endpoints.
- **Workflow Engine (BullMQ)**: Manages an asynchronous processing queue using Redis as a message broker.
- **Background Workers**: Dedicated processes that consume jobs from the queue and execute the multi-step pipeline.
- **AI Engine (Python/FastAPI)**: Specialized service that performs the actual AI computations (Feature extraction, Embeddings, etc.).

---

## 🛠️ Tech Stack

- **API Frameworks**: [Express](https://expressjs.com/) (Node.js), [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Job Queuing**: [BullMQ](https://docs.bullmq.io/)
- **Databases**: [MongoDB](https://www.mongodb.com/) (via Mongoose), [Redis](https://redis.io/) (via `redis` client)
- **Environment**: Node.js 18+, Python 3.9+
- **Integrations**: Axios for inter-service communication

---

## 🚦 Asynchronous Pipeline

The core of NeuroPlay is a 5-step processing pipeline executed for every simulation job:

1.  **🎥 Video Processing**: AI-driven analysis of raw video inputs.
2.  **🧠 Feature Extraction**: Extracting meaningful data points from the processed video.
3.  **📊 Embedding Generation**: Converting features into multi-dimensional vectors.
4.  **📦 Clustering**: Grouping related features and patterns.
5.  **🎮 Simulation**: Final computation based on the aggregated data.

---

## 🔗 API Endpoints

### 🟢 Central API (Backend)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status |
| `GET` | `/api` | API discovery root |
| `GET` | `/api/job/:id` | Retrieve status, progress, and results of a specific Job |
| `POST` | `/api/test/test-job` | Create a new simulation pipeline job (accepts `input` JSON) |

### 🔵 AI Engine (Python)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status |
| `POST` | `/ai/execute` | Execute a specific AI processing step for a given job |

---

## 🚀 Getting Started

### 1. Prerequisites

- MongoDB up and running
- Redis server active

### 2. Environment Configuration

Each service requires a `.env` file. The backend now validates mandatory variables on startup.

**Backend (`/backend/.env`):**
```env
PORT=5000
MONGO_URI=mongodb://127.0.0.1:27017/neuroplay
REDIS_URL=redis://127.0.0.1:6379
```

**AI Engine (`/ai-engine/.env`):**
```env
PORT=8000
```

### 3. Execution Commands

#### Start the API & Workers
```bash
# In /backend
npm install
npm run dev      # Starts the API server
npm run worker   # Starts the background queue processors (Worker)

# In /ai-engine
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## 📁 Directory Structure

```text
core-backend/
├── ai-engine/         # Python/FastAPI Service (AI Step Execution)
├── backend/           # Node.js/Express Service
│   └── src/
│       ├── config/    # Environment and Database configuration
│       ├── core/      # Core logic (Jobs, Queue, Pipeline, Workers)
│       ├── modules/   # API Route controllers
│       └── integrations/ # Inter-service communication
├── infrastructure/    # Deployment configs
└── shared/            # Common schemas
```

---

## 📝 License

This project is licensed under the ISC License.
