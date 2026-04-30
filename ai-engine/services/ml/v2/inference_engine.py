import os
import numpy as np
import torch
import torch.nn as nn
import faiss
import joblib

from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId

# ==============================
# ENV
# ==============================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["segments"]

# ==============================
# PATHS
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

MODEL_DIR = os.path.join(ROOT_DIR, "models", "v2")
FAISS_DIR = os.path.join(ROOT_DIR, "faiss", "v2")
CLUSTER_DIR = os.path.join(ROOT_DIR, "clusters", "v2")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ==============================
# MODEL
# ==============================
class AutoEncoder(nn.Module):
    def __init__(self, input_dim=20, latent_dim=8):
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, latent_dim)
        )

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, input_dim),
            nn.Sigmoid()
        )

    def encode(self, x):
        return self.encoder(x)


# ==============================
# ENGINE
# ==============================
class InferenceEngine:
    def __init__(self, domain):
        self.domain = domain

        print(f"⚡ Initializing engine for: {domain}")

        self.model = self._load_model()
        self.index = self._load_faiss()
        self.clusters = self._load_clusters()
        self.scaler = self._load_scaler()
        self.mapping = self._load_mapping()  # 🔥 NEW

    def _load_model(self):
        path = os.path.join(MODEL_DIR, f"autoencoder_{self.domain}.pt")
        model = AutoEncoder().to(DEVICE)
        model.load_state_dict(torch.load(path, map_location=DEVICE))
        model.eval()
        return model

    def _load_faiss(self):
        path = os.path.join(FAISS_DIR, f"faiss_{self.domain}.index")
        return faiss.read_index(path)

    def _load_clusters(self):
        path = os.path.join(CLUSTER_DIR, f"clusters_{self.domain}.npz")
        data = np.load(path)
        return {
            "labels": data["labels"],
            "confidence": data["confidence"]
        }

    def _load_scaler(self):
        path = os.path.join(MODEL_DIR, f"scaler_{self.domain}.pkl")
        return joblib.load(path)

    def _load_mapping(self):
        path = os.path.join(FAISS_DIR, f"mapping_{self.domain}.npy")
        return np.load(path, allow_pickle=True)

    # ==============================
    # FETCH SEGMENTS (Mongo)
    # ==============================
    def fetch_segments(self, segment_ids):
        object_ids = [ObjectId(sid) for sid in segment_ids]

        docs = list(collection.find({
            "_id": {"$in": object_ids}
        }))

        # preserve order
        doc_map = {str(doc["_id"]): doc for doc in docs}

        return [doc_map.get(sid) for sid in segment_ids]

    # ==============================
    # FEATURE BUILDER
    # ==============================
    def build_feature_vector(self, player_state, prev_state=None):
        motion = player_state.get("motion_intensity", 0)
        variance = player_state.get("motion_variance", 0)
        brightness = player_state.get("brightness_avg", 0)
        flash = player_state.get("flash_count", 0)
        edge = player_state.get("edge_density_avg", 0)
        entropy = player_state.get("entropy_avg", 0)

        features = [
            motion, variance, brightness, flash, edge, entropy,
            motion / (variance + 1e-5),
            1 / (variance + 1e-5),
            brightness * edge,
            entropy * motion,
            flash / 5.0,
            motion * brightness,
            edge * entropy,
            motion * entropy,
            motion ** 2,
            entropy ** 2,
        ]

        if prev_state:
            prev_motion = prev_state.get("motion_intensity", 0)
            prev_entropy = prev_state.get("entropy_avg", 0)

            features.extend([
                motion - prev_motion,
                entropy - prev_entropy
            ])
        else:
            features.extend([0, 0])

        if len(features) < 20:
            features.extend([0] * (20 - len(features)))

        return np.array(features[:20], dtype=np.float32)

    # ==============================
    # INFERENCE
    # ==============================
    def infer(self, player_state, prev_state=None):
        # Feature
        features = self.build_feature_vector(player_state, prev_state)

        # Scale
        features = self.scaler.transform([features])[0].astype(np.float32)

        # Embedding
        tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            embedding = self.model.encode(tensor).cpu().numpy()

        # FAISS search
        distances, indices = self.index.search(embedding.astype("float32"), 5)

        indices = indices[0]
        distances = distances[0]

        # 🔥 Map indices → segment_ids
        segment_ids = [str(self.mapping[i]) for i in indices]

        # 🔥 Fetch Mongo docs
        segments = self.fetch_segments(segment_ids)

        results = []

        for i, seg in enumerate(segments):
            if seg is None:
                continue

            idx = indices[i]

            results.append({
                "segment_id": segment_ids[i],
                "cluster_id": int(self.clusters["labels"][idx]),
                "confidence": float(self.clusters["confidence"][idx]),
                "distance": float(distances[i]),
                "player_state": seg.get("input_data", {}).get("player_state", {}),
                "events": seg.get("input_data", {}).get("events", [])
            })

        return {
            "embedding": embedding.tolist(),
            "similar_segments": results
        }


# ==============================
# TEST
# ==============================
if __name__ == "__main__":
    domains = ["blackops", "modern_warfare"]

    sample = {
        "motion_intensity": 0.06,
        "motion_variance": 0.002,
        "brightness_avg": 0.15,
        "flash_count": 0,
        "edge_density_avg": 0.01,
        "entropy_avg": 0.63
    }

    for d in domains:
        print(f"\n==============================")
        print(f"🚀 Testing domain: {d}")

        engine = InferenceEngine(d)
        result = engine.infer(sample)

        print("\n🧠 RESULT:")
        for k, v in result.items():
            print(k, ":", v)