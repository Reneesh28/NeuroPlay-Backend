import sys
import os

# Ensure project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

from models.autoencoder import Autoencoder


def train(
    dataset_path="dataset.npy",
    model_path="models/model.pt",
    epochs=50,
    batch_size=16,
    lr=1e-3
):
    print("📂 Loading dataset...")

    data = np.load(dataset_path)
    data = torch.tensor(data, dtype=torch.float32)

    print(f"✅ Dataset loaded: {data.shape}")

    model = Autoencoder()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    print("🚀 Starting training...\n")

    for epoch in range(epochs):
        perm = torch.randperm(data.size(0))
        epoch_loss = 0

        for i in range(0, data.size(0), batch_size):
            batch_idx = perm[i:i + batch_size]
            batch = data[batch_idx]

            optimizer.zero_grad()

            output = model(batch)
            loss = criterion(output, batch)

            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        print(f"Epoch [{epoch+1}/{epochs}] Loss: {epoch_loss:.6f}")

    # Save model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    torch.save(model.state_dict(), model_path)

    print(f"\n💾 Model saved to: {model_path}")


if __name__ == "__main__":
    train()