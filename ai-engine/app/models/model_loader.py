import os
import logging
import torch

from services.ml.v2.inference_engine import AutoEncoder  # 🔥 correct model

logger = logging.getLogger(__name__)

_model_cache = {}


def _get_model_path(domain: str) -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(
        base_dir,
        "services",
        "models",
        "v2",
        f"autoencoder_{domain}.pt"
    )


def load_model(domain: str):
    if domain in _model_cache:
        return _model_cache[domain]

    model_path = _get_model_path(domain)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")

    logger.info(f"🔄 Loading model for domain: {domain}")

    model = AutoEncoder(input_dim=20, latent_dim=8)

    state_dict = torch.load(model_path, map_location=torch.device("cpu"))
    model.load_state_dict(state_dict)

    model.eval()

    _model_cache[domain] = model

    logger.info("✅ Model loaded successfully")

    return model


def get_model(domain: str):
    return load_model(domain)