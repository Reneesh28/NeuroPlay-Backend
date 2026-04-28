import logging
import sys
import os

# Add ai-engine root to path to ensure 'features' is importable if not already
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.core.errors import MLError, PartialExecutionTrigger
from app.core.execution_mode import ExecutionMode
from features.feature_extraction import run_feature_extraction

logger = logging.getLogger(__name__)


def run(input_data: dict, context: dict, execution_mode: str) -> tuple:
    trace_id = context.get("trace_id", "unknown")

    current_mode = execution_mode

    if current_mode == ExecutionMode.FULL:
        try:
            logger.info(f"[Trace: {trace_id}] Feature FULL")
            # input_data is the segment
            result = run_feature_extraction(input_data)
            return result, ExecutionMode.FULL

        except (MLError, PartialExecutionTrigger):
            current_mode = ExecutionMode.PARTIAL
        except Exception as e:
            logger.error(f"[Trace: {trace_id}] Error in Feature FULL: {str(e)}")
            current_mode = ExecutionMode.PARTIAL

    if current_mode == ExecutionMode.PARTIAL:
        try:
            logger.info(f"[Trace: {trace_id}] Feature PARTIAL")
            # Simple fallback for partial mode
            raw = {"movement_speed": 0.5, "aim_stability": 0.5} # Minimal features
            return {
                "features": raw,
                "normalized_features": raw,
                "ml_input": [0.5, 0.5, 0, 0, 0, 0, 0],
                "partial": True
            }, ExecutionMode.PARTIAL

        except Exception:
            current_mode = ExecutionMode.FALLBACK

    logger.info(f"[Trace: {trace_id}] Feature FALLBACK")

    return {
        "features": {},
        "normalized_features": {},
        "ml_input": [0.0] * 7,
        "fallback": True,
        "confidence": 0.0
    }, ExecutionMode.FALLBACK