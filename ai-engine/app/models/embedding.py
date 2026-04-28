import torch
from typing import List

from app.models.model_loader import get_model


def generate_embedding(ml_input: List[float]) -> List[float]:
    """
    Convert 20D ml_input → 8D embedding
    """

    if not isinstance(ml_input, list):
        raise ValueError("ml_input must be a list")

    if len(ml_input) != 20:
        raise ValueError(f"Expected 20D input, got {len(ml_input)}")

    # Convert to tensor
    x = torch.tensor(ml_input, dtype=torch.float32).unsqueeze(0)

    model = get_model()

    with torch.no_grad():
        embedding = model.encode(x)

    return embedding.squeeze(0).tolist()