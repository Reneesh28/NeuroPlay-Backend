import os
import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib

# ==============================
# 🔧 PATH CONFIG
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

DATA_PATH = os.path.join(ROOT_DIR, "data", "dataset.npy")
MODEL_DIR = os.path.join(ROOT_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ==============================
# 🔹 LOAD DATASET
# ==============================
X = np.load(DATA_PATH)
print(f"📊 Loaded dataset: {X.shape}")

# ==============================
# 🔹 NORMALIZATION
# ==============================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

# ==============================
# 🔹 TENSOR
# ==============================
X_tensor = torch.tensor(X_scaled, dtype=torch.float32)

# ==============================
# 🔹 MODEL
# ==============================
LATENT_DIM = 4  # 🔥 UPDATED

class Autoencoder(nn.Module):
    def __init__(self, input_dim=6, latent_dim=LATENT_DIM):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, input_dim)
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))

model = Autoencoder()

criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

# ==============================
# 🔹 TRAIN
# ==============================
epochs = 40
batch_size = 256
N = X_tensor.size(0)

for epoch in range(epochs):
    perm = torch.randperm(N)
    epoch_loss = 0

    for i in range(0, N, batch_size):
        batch = X_tensor[perm[i:i+batch_size]]

        optimizer.zero_grad()
        loss = criterion(model(batch), batch)
        loss.backward()
        optimizer.step()

        epoch_loss += loss.item() * batch.size(0)

    epoch_loss /= N
    scheduler.step()

    print(f"Epoch {epoch+1}/{epochs} | Loss: {epoch_loss:.5f}")

# ==============================
# 🔹 SAVE
# ==============================
torch.save(model.state_dict(), os.path.join(MODEL_DIR, "model.pt"))
print("💾 Model saved")