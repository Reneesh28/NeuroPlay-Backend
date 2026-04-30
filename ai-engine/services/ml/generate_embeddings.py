import os
import torch
import torch.nn as nn
import numpy as np
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

DATA_PATH = os.path.join(ROOT_DIR, "data", "dataset.npy")
MODEL_PATH = os.path.join(ROOT_DIR, "models", "model.pt")
SCALER_PATH = os.path.join(ROOT_DIR, "models", "scaler.pkl")
OUTPUT_PATH = os.path.join(ROOT_DIR, "data", "embeddings.npy")

LATENT_DIM = 4  # 🔥 MUST MATCH

# ==============================
# 🔹 LOAD DATA
# ==============================
X = np.load(DATA_PATH)
scaler = joblib.load(SCALER_PATH)
X_scaled = scaler.transform(X)

# ==============================
# 🔹 MODEL
# ==============================
class Autoencoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(6, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, LATENT_DIM)
        )
        self.decoder = nn.Sequential(
            nn.Linear(LATENT_DIM, 16),
            nn.ReLU(),
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, 6)
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))

model = Autoencoder()
model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()

# ==============================
# 🔹 GENERATE EMBEDDINGS
# ==============================
with torch.no_grad():
    embeddings = model.encoder(
        torch.tensor(X_scaled, dtype=torch.float32)
    ).numpy()

np.save(OUTPUT_PATH, embeddings)
print(f"💾 Saved embeddings: {embeddings.shape}")