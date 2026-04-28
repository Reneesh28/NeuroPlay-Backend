import logging
from typing import Dict, Any

from app.core.execution_mode import ExecutionMode
from app.core.errors import MLError, PartialExecutionTrigger
from app.models.embedding import generate_embedding

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 8


def _extract_ml_input(input_data: Dict[str, Any]) -> list:
    """
    Safely extract ml_input from different possible structures
    """
    # Handle normalized loader structure
    if "input_data" in input_data:
        return input_data["input_data"].get("ml_input")

    # Handle stored feature output
    if "data" in input_data:
        return input_data["data"].get("ml_input")

    # Direct pass (fallback)
    return input_data.get("ml_input")


def run(input_data: Dict[str, Any], context: Dict[str, Any], execution_mode: str) -> tuple:
    trace_id = context.get("trace_id", "unknown")

    current_mode = execution_mode

    # ======================
    # FULL MODE
    # ======================
    if current_mode == ExecutionMode.FULL:
        try:
            logger.info(f"[Trace: {trace_id}] Embedding FULL")

            # 🔥 Extract ml_input safely
            ml_input = _extract_ml_input(input_data)

            if not ml_input:
                logger.warning(f"[Trace: {trace_id}] ml_input missing → using default vector")
                ml_input = [0.0] * 20

            # 🔥 Generate embedding
            embedding = generate_embedding(ml_input)

            # 🔥 Validate output
            if len(embedding) != EMBEDDING_DIM:
                raise ValueError(f"Invalid embedding dimension: {len(embedding)}")

            output = {
                "embedding": embedding,
                "embedding_dim": EMBEDDING_DIM
            }

            print("EMBEDDING OUTPUT:", output)  # Debug (can remove later)

            return output, ExecutionMode.FULL

        except (MLError, PartialExecutionTrigger):
            logger.warning(f"[Trace: {trace_id}] Switching to PARTIAL mode")
            current_mode = ExecutionMode.PARTIAL

        except Exception as e:
            logger.error(f"[Trace: {trace_id}] Embedding FULL error: {str(e)}")
            current_mode = ExecutionMode.PARTIAL

    # ======================
    # PARTIAL MODE
    # ======================
    if current_mode == ExecutionMode.PARTIAL:
        try:
            logger.info(f"[Trace: {trace_id}] Embedding PARTIAL")

            return {
                "embedding": [0.1] * EMBEDDING_DIM,
                "embedding_dim": EMBEDDING_DIM,
                "partial": True
            }, ExecutionMode.PARTIAL

        except Exception:
            current_mode = ExecutionMode.FALLBACK

    # ======================
    # FALLBACK MODE
    # ======================
    logger.info(f"[Trace: {trace_id}] Embedding FALLBACK")

    return {
        "embedding": [0.0] * EMBEDDING_DIM,
        "embedding_dim": EMBEDDING_DIM,
        "fallback": True,
        "confidence": 0.0
    }, ExecutionMode.FALLBACK