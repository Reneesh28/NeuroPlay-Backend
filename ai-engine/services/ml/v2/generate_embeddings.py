import os
import numpy as np
import torch
import torch.nn as nn

# ==============================
# PATHS
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

DATA_DIR = os.path.join(ROOT_DIR, "data", "v2")
MODEL_DIR = os.path.join(ROOT_DIR, "models", "v2")
EMBED_DIR = os.path.join(ROOT_DIR, "embeddings", "v2")

os.makedirs(EMBED_DIR, exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ==============================
# MODEL (MATCH TRAINING EXACTLY)
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

    def forward(self, x):
        z = self.encoder(x)
        x_hat = self.decoder(z)
        return x_hat, z

    def encode(self, x):
        return self.encoder(x)


# ==============================
# GENERATE EMBEDDINGS
# ==============================
def generate_embeddings(domain):
    print(f"\n🚀 Generating embeddings for: {domain}")

    dataset_path = os.path.join(DATA_DIR, f"dataset_{domain}.npy")
    model_path = os.path.join(MODEL_DIR, f"autoencoder_{domain}.pt")

    if not os.path.exists(dataset_path):
        print("❌ Dataset missing")
        return

    if not os.path.exists(model_path):
        print("❌ Model missing")
        return

    # ------------------------------
    # LOAD DATA
    # ------------------------------
    data = np.load(dataset_path)
    print("📊 Dataset shape:", data.shape)

    tensor_data = torch.tensor(data, dtype=torch.float32).to(DEVICE)

    # ------------------------------
    # LOAD MODEL
    # ------------------------------
    model = AutoEncoder().to(DEVICE)
    model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    model.eval()

    # ------------------------------
    # GENERATE EMBEDDINGS
    # ------------------------------
    with torch.no_grad():
        embeddings = model.encode(tensor_data).cpu().numpy()

    print("📊 Embeddings shape:", embeddings.shape)

    # ==============================
    # VALIDATION (CRITICAL)
    # ==============================
    print("\n🔍 Embedding Stats:")
    print("Mean:", embeddings.mean())
    print("Std:", embeddings.std())
    print("Variance per dim:", np.var(embeddings, axis=0))

    # ==============================
    # SIMILARITY TEST
    # ==============================
    print("\n🧪 Similarity Test:")

    idx = 100  # sample point
    query = embeddings[idx]

    distances = np.linalg.norm(embeddings - query, axis=1)
    nearest = np.argsort(distances)[:5]

    print(f"Query index: {idx}")
    print("Nearest indices:", nearest)
    print("Distances:", distances[nearest])

    # ==============================
    # SAVE EMBEDDINGS
    # ==============================
    save_path = os.path.join(EMBED_DIR, f"embeddings_{domain}.npy")
    np.save(save_path, embeddings)

    print(f"\n💾 Embeddings saved → {save_path}")


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    domains = ["blackops", "modern_warfare"]

    for d in domains:
        generate_embeddings(d)