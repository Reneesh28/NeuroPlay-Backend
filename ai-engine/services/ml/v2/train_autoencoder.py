import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from torch.optim.lr_scheduler import ReduceLROnPlateau

# ==============================
# PATHS
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

DATA_DIR = os.path.join(ROOT_DIR, "data", "v2")
MODEL_DIR = os.path.join(ROOT_DIR, "models", "v2")

os.makedirs(MODEL_DIR, exist_ok=True)

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
            nn.Sigmoid()  # IMPORTANT (since MinMax scaled)
        )

    def forward(self, x):
        z = self.encoder(x)
        x_hat = self.decoder(z)
        return x_hat, z

    def encode(self, x):
        return self.encoder(x)


# ==============================
# TRAIN FUNCTION
# ==============================
def train_model(domain):
    print(f"\n🚀 Training for domain: {domain}")

    dataset_path = os.path.join(DATA_DIR, f"dataset_{domain}.npy")

    if not os.path.exists(dataset_path):
        print("❌ Dataset not found")
        return

    # ------------------------------
    # LOAD DATA
    # ------------------------------
    data = np.load(dataset_path)
    print("📊 Dataset shape:", data.shape)

    tensor_data = torch.tensor(data, dtype=torch.float32)

    dataset = TensorDataset(tensor_data)
    loader = DataLoader(dataset, batch_size=64, shuffle=True)

    # ------------------------------
    # MODEL SETUP
    # ------------------------------
    model = AutoEncoder().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    scheduler = ReduceLROnPlateau(optimizer, patience=5, factor=0.5)

    # ------------------------------
    # TRAINING
    # ------------------------------
    epochs = 40

    for epoch in range(epochs):
        total_loss = 0

        for batch in loader:
            x = batch[0].to(DEVICE)

            optimizer.zero_grad()

            recon, z = model(x)
            loss = criterion(recon, x)

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        scheduler.step(total_loss)

        print(f"Epoch {epoch+1}/{epochs} | Loss: {total_loss:.4f}")

    # ------------------------------
    # SAVE MODEL
    # ------------------------------
    model_path = os.path.join(MODEL_DIR, f"autoencoder_{domain}.pt")
    torch.save(model.state_dict(), model_path)

    print(f"💾 Model saved → {model_path}")


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    domains = ["blackops", "modern_warfare"]

    for domain in domains:
        train_model(domain)