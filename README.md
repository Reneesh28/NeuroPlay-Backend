# NeuroPlay Core Backend 🧠🎮

The high-performance, multi-service backend infrastructure for the NeuroPlay ecosystem. This repository houses the central API gateways, AI processing engines, and real-time connectivity services.

## 🏗️ Architecture Overview

NeuroPlay Core Backend follows a microservice-inspired architecture designed for scalability and separation of concerns:

- **Central API (Node.js)**: Built with Express, this service handles user management, persistence, and serves as the primary gateway for clients.
- **AI Engine (Python)**: A FastAPI-driven service dedicated to heavy computational tasks and AI-driven logic.
- **Data Layer**: Utilizes MongoDB for document storage and Redis for high-speed caching and real-time state management.

---

## 🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (v3.9+)
- [MongoDB](https://www.mongodb.com/) (Local or Atlas)
- [Redis](https://redis.io/)

### 1. Central API Setup

```bash
cd backend
npm install
cp .env.example .env  # Configure your environment variables
npm run dev
```

### 2. AI Engine Setup

```bash
cd ai-engine
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## 📁 Directory Structure

```text
core-backend/
├── ai-engine/         # Python/FastAPI Service (AI Logic)
├── backend/           # Node.js/Express Service (Core API)
├── infrastructure/    # Deployment and Orchestration configs
├── shared/            # Common schemas and utilities
├── tests/             # Integration and E2E tests
└── scripts/           # Automation and maintenance scripts
```

---

## 🛠️ Tech Stack

- **Frameworks**: Express (Node.js), FastAPI (Python)
- **Databases**: MongoDB (via Mongoose), Redis (via ioredis)
- **Environment**: Node.js, Python 3.x
- **Development**: Nodemon, Uvicorn

---

## 🛡️ Environment Configuration

Ensure each service has its own `.env` file with at least the following:

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

---

## 📝 License

This project is licensed under the ISC License.
