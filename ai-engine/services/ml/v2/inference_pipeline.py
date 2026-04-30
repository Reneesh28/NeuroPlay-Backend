import os
import numpy as np
import torch
import torch.nn as nn
import faiss
import joblib

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
# LOADERS
# ==============================
def load_model(domain):
    model_path = os.path.join(MODEL_DIR, f"autoencoder_{domain}.pt")

    model = AutoEncoder().to(DEVICE)
    model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    model.eval()

    return model


def load_faiss(domain):
    index_path = os.path.join(FAISS_DIR, f"faiss_{domain}.index")
    return faiss.read_index(index_path)


def load_clusters(domain):
    cluster_path = os.path.join(CLUSTER_DIR, f"clusters_{domain}.npz")

    data = np.load(cluster_path)

    return {
        "labels": data["labels"],
        "confidence": data["confidence"]
    }


def load_scaler(domain):
    scaler_path = os.path.join(MODEL_DIR, f"scaler_{domain}.pkl")
    return joblib.load(scaler_path)


# ==============================
# FEATURE BUILDER
# ==============================
def build_feature_vector(player_state, prev_state=None):
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
# MAIN INFERENCE
# ==============================
def run_inference(domain, player_state, prev_state=None):
    print(f"\n🚀 Running inference for: {domain}")

    model = load_model(domain)
    index = load_faiss(domain)
    clusters = load_clusters(domain)
    scaler = load_scaler(domain)

    # ------------------------------
    # STEP 1: Feature
    # ------------------------------
    features = build_feature_vector(player_state, prev_state)

    # ------------------------------
    # STEP 2: SCALE (CRITICAL)
    # ------------------------------
    features = scaler.transform([features])[0].astype(np.float32)

    # ------------------------------
    # STEP 3: Embedding
    # ------------------------------
    tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        embedding = model.encode(tensor).cpu().numpy()

    # ------------------------------
    # STEP 4: FAISS SEARCH
    # ------------------------------
    distances, indices = index.search(embedding.astype("float32"), 5)

    # ------------------------------
    # STEP 5: CLUSTER ASSIGNMENT
    # ------------------------------
    nearest_idx = indices[0][0]
    cluster_id = int(clusters["labels"][nearest_idx])
    confidence = float(clusters["confidence"][nearest_idx])

    # ------------------------------
    # OUTPUT
    # ------------------------------
    result = {
        "embedding": embedding.tolist(),
        "nearest_indices": indices[0].tolist(),
        "distances": distances[0].tolist(),
        "cluster_id": cluster_id,
        "confidence": confidence
    }

    return result


# ==============================
# TEST
# ==============================
if __name__ == "__main__":
    sample_state = {
        "motion_intensity": 0.06,
        "motion_variance": 0.002,
        "brightness_avg": 0.15,
        "flash_count": 0,
        "edge_density_avg": 0.01,
        "entropy_avg": 0.63
    }

    output = run_inference("blackops", sample_state)

    print("\n🧠 RESULT:")
    for k, v in output.items():
        print(f"{k}: {v}")