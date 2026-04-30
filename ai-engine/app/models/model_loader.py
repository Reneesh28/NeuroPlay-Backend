import os
import logging
import torch

from app.models.autoencoder import Autoencoder  # ✅ FIXED IMPORT

logger = logging.getLogger(__name__)

# Singleton instance
_model = None


def _get_model_path() -> str:
    """
    Resolve path to trained model:
    ai-engine/models/model.pt
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_dir, "models", "model.pt")


def load_model() -> Autoencoder:
    """
    Load model once (singleton)
    """
    global _model

    if _model is not None:
        return _model

    model_path = _get_model_path()

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")

    logger.info("🔄 Loading Autoencoder model...")

    model = Autoencoder()

    # Load weights (CPU-safe)
    state_dict = torch.load(model_path, map_location=torch.device("cpu"))
    model.load_state_dict(state_dict)

    model.eval()  # 🔥 REQUIRED for inference

    _model = model

    logger.info("✅ Model loaded successfully")

    return _model


def get_model() -> Autoencoder:
    """
    Public accessor
    """
    return load_model()