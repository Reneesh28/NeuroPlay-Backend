# NeuroPlay AI Engine 🧠🤖

The **AI Engine** is a high-performance Python microservice built with **FastAPI**. It is responsible for executing the core Machine Learning pipeline for the NeuroPlay ecosystem, transforming raw gameplay video and telemetry data into deeply analyzed behavioral simulations.

---

## 🏗️ The 5-Step ML Pipeline

The AI Engine processes gameplay data through a stateful 5-step pipeline:

1. **Video Processing (`video_processing`)**: Ingests raw video/telemetry and normalizes it.
2. **Feature Extraction (`feature_extraction`)**: Calculates key gameplay metrics across multiple dimensions (e.g., `motion_intensity`, `brightness`, `flash_count`, `entropy`).
3. **Embedding Generation (`embedding_generation`)**: Uses a PyTorch **AutoEncoder** to compress 20-dimensional feature vectors down to 8-dimensional dense embeddings.
4. **Clustering (`clustering`)**: Uses **HDBSCAN** (unsupervised learning) to group similar embeddings into distinct behavioral clusters (e.g., standard gameplay, firefights, menus).
5. **Simulation (`simulation`)**: Uses **FAISS** (Facebook AI Similarity Search) to perform ultra-fast nearest-neighbor lookups, matching new gameplay segments against the indexed historical clusters to simulate outcomes.

---

## 📊 V2 Machine Learning Models

The current generation of models (`v2`) operates on specific game domains (e.g., `blackops`, `modern_warfare`). 

### Behavioral Clusters
The HDBSCAN algorithm autonomously identifies clusters based on mathematical similarity. For example:
- **High-Action Clusters**: Characterized by high `motion_intensity` and high `flash_count`.
- **Standard Gameplay Clusters**: Characterized by moderate motion and low/zero flash counts.
- **Static Screens / Menus**: Characterized by near-zero motion and extreme (high or low) brightness values.

*Note: HDBSCAN uses the label `-1` to denote "noise" (outliers that don't fit into any cluster).*

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- CUDA toolkit (Optional, for GPU-accelerated PyTorch)

### Installation & Setup

1. **Navigate to the directory**:
   ```bash
   cd core-backend/ai-engine
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Ensure you have a `.env` file in the root of `ai-engine`:
   ```env
   PORT=8000
   MONGO_URI=mongodb://127.0.0.1:27017/neuroplay
   DB_NAME=neuroplay
   ```

### Running the API Server

Start the FastAPI application using Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```
*The API will be available at `http://localhost:8000`.*

---

## 📁 Directory Structure

- `app/`: FastAPI application code (routing, schemas, controllers).
- `services/ml/v2/`: Contains the core Machine Learning logic for V2:
  - `inference_engine.py`: The main engine orchestrating the AutoEncoder, FAISS index, and Cluster mappings.
  - `clustering.py`: Script for generating HDBSCAN clusters and PCA visualization plots.
- `features/`: Logic for extracting visual and telemetry features from raw data.
- `training/`: Scripts and notebooks for training the AutoEncoder models.
- `services/data/v2/`, `services/models/v2/`, `services/embeddings/v2/`, `services/clusters/v2/`: Repositories for the generated NumPy arrays, PyTorch models, and FAISS indices.
