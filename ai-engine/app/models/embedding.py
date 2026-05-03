import torch
from typing import List

from app.models.model_loader import get_model


def generate_embedding(ml_input: List[float], domain: str = "blackops") -> List[float]:
    """
    Convert 20D → 8D embedding
    """

    if not isinstance(ml_input, list):
        raise ValueError("ml_input must be a list")

    if len(ml_input) != 20:
        raise ValueError(f"Expected 20D input, got {len(ml_input)}")

    x = torch.tensor(ml_input, dtype=torch.float32).unsqueeze(0)

    # 🔥 FIX 3 → pass domain
    model = get_model(domain)

    with torch.no_grad():
        embedding = model.encoder(x)

    return embedding.squeeze(0).tolist()