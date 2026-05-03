import logging
from typing import Dict, Any, List

from app.core.execution_mode import ExecutionMode
from app.core.errors import MLError, PartialExecutionTrigger
from app.models.embedding import generate_embedding

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 8
EXPECTED_INPUT_DIM = 20


def _extract_ml_input(input_data: Dict[str, Any]) -> List[float]:
    """
    Safely extract ml_input from different possible structures.
    """
    if "input_data" in input_data:
        return input_data["input_data"].get("ml_input")

    if "data" in input_data:
        return input_data["data"].get("ml_input")

    return input_data.get("ml_input")


def _validate_ml_input(ml_input: List[float]):
    if ml_input is None:
        raise ValueError("ml_input is missing")

    if not isinstance(ml_input, list):
        raise ValueError("ml_input must be a list")

    if len(ml_input) != EXPECTED_INPUT_DIM:
        raise ValueError(f"ml_input must be length {EXPECTED_INPUT_DIM}, got {len(ml_input)}")


def run(input_data: Dict[str, Any], context: Dict[str, Any], execution_mode: str) -> tuple:
    trace_id = context.get("trace_id", "unknown")
    domain = context.get("domain", "blackops")  # 🔥 FIX 3

    current_mode = execution_mode

    # ======================
    # FULL MODE
    # ======================
    if current_mode == ExecutionMode.FULL:
        try:
            logger.info(f"[Trace: {trace_id}] Embedding FULL")

            ml_input = _extract_ml_input(input_data)

            if not ml_input:
                raise ValueError("ml_input missing")

            print("ML INPUT:", ml_input)

            # 🔥 FIX 3 → pass domain
            embedding = generate_embedding(ml_input, domain)

            print("EMBEDDING:", embedding)

            if len(embedding) != EMBEDDING_DIM:
                raise ValueError(f"Invalid embedding dimension: {len(embedding)}")

            return {
                "embedding": embedding,
                "embedding_dim": EMBEDDING_DIM
            }, ExecutionMode.FULL

        except Exception as e:
            logger.error(f"[Trace: {trace_id}] Embedding FAILED: {str(e)}")
            raise e  # 🔥 DO NOT HIDE ERROR

    # ======================
    # PARTIAL MODE
    # ======================
    try:
        logger.info(f"[Trace: {trace_id}] Embedding PARTIAL")

        return {
            "embedding": [0.1] * EMBEDDING_DIM,
            "embedding_dim": EMBEDDING_DIM,
            "partial": True
        }, ExecutionMode.PARTIAL

    except Exception:
        logger.error(f"[Trace: {trace_id}] Embedding PARTIAL failed")

    # ======================
    # FALLBACK MODE
    # ======================
    logger.info(f"[Trace: {trace_id}] Embedding FALLBACK")

    return {
        "embedding": [0.0] * EMBEDDING_DIM,
        "embedding_dim": EMBEDDING_DIM,
        "fallback": True
    }, ExecutionMode.FALLBACK