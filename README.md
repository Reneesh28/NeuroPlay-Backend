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

### 📚 Core Services Documentation

For detailed service-specific documentation, please refer to their respective README files:

| Service | Runtime | Documentation |
| :--- | :--- | :--- |
| **Backend API & Worker** | Node.js / Express / BullMQ | 📖 [Backend README](./backend/README.md) |
| **AI Engine & ML Pipeline** | Python / FastAPI / PyTorch | 📖 [AI Engine README](./ai-engine/README.md) |

---

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| API Framework | [Express v5](https://expressjs.com/) (Node.js) |
| AI Service | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.9+) |
| Machine Learning | PyTorch, FAISS, HDBSCAN, Scikit-learn |
| Job Queue | [BullMQ](https://docs.bullmq.io/) |
| Queue Broker | [Redis](https://redis.io/) via `ioredis` |
| Database | [MongoDB](https://www.mongodb.com/) via Mongoose |
| File Uploads | [Multer](https://github.com/expressjs/multer) |
| Inter-service | [Axios](https://axios-http.com/) |

---

## 🚦 5-Step Processing Pipeline

Every simulation job is processed through a sequential, stateful pipeline. Each step is executed by the AI Engine and its result is persisted to MongoDB before the next step starts.

| Step | Name | Description |
| :---: | :--- | :--- |
| 1 | `video_processing` | AI-driven ingestion and analysis of raw video inputs |
| 2 | `feature_extraction` | Extracting meaningful data points (motion, brightness, entropy) |
| 3 | `embedding_generation` | Converting features into 8-dimensional dense vectors (AutoEncoder) |
| 4 | `clustering` | Grouping behavioral patterns via HDBSCAN clustering |
| 5 | `simulation` | FAISS similarity search against historical vectors for outcome prediction |

> **Note on V2 Models:** The AI Engine is currently running V2 models capable of dynamically categorizing standard gameplay, high-action combat (high motion/flashes), and non-gameplay states (menus/loading screens) purely through unsupervised clustering. See the [AI Engine README](./ai-engine/README.md) for more details.

---

## 🚀 Quick Start Guide

### 1. Prerequisites

- **Node.js** v18+
- **Python** 3.9+
- **MongoDB** running (local or Atlas)
- **Redis** server running (local or Docker)

### 2. Environment Configuration

Ensure both services have their `.env` files configured.

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
MONGO_URI=mongodb://127.0.0.1:27017/neuroplay
DB_NAME=neuroplay
```

### 3. Running the Stack

To run the full end-to-end pipeline, you need **three** terminal windows:

**Terminal 1: Node.js Express API**
```bash
cd backend
npm install
npm run dev
```

**Terminal 2: Node.js BullMQ Worker**
```bash
cd backend
node worker.js
```

**Terminal 3: Python FastAPI AI Engine**
```bash
cd ai-engine
python -m venv venv
venv\Scripts\activate   # Windows (use `source venv/bin/activate` for Mac/Linux)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## 📁 Directory Structure

```text
core-backend/
├── README.md                       # This file
├── backend/                        # Node.js API & BullMQ Worker
│   ├── README.md                   # Backend specific documentation
│   ├── server.js                   # Express server entry
│   ├── worker.js                   # BullMQ consumer entry
│   └── src/                        # Core backend logic
│
├── ai-engine/                      # Python AI Processing Service
│   ├── README.md                   # AI Engine specific documentation
│   ├── app/                        # FastAPI server
│   ├── services/                   # FAISS, Models, and NumPy data
│   └── features/                   # ML Feature extraction logic
│
├── infrastructure/                 # Deployment configs (Docker, CI/CD)
├── shared/                         # Common schemas across services
└── scripts/                        # Utility scripts
```

---

## 🐛 Troubleshooting

* **Worker fails with `Operation buffering timed out`**: Ensure MongoDB is reachable before starting the worker.
* **`BullMQ: maxRetriesPerRequest must be null`**: Check your Redis config to ensure retries are null (handled automatically in `backend/src/config/redis.js`).
* **Jobs stuck in waiting**: Ensure the `node worker.js` process is actively running.

## 📝 License

This project is licensed under the **ISC License**.
