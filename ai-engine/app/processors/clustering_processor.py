import logging
from app.core.execution_mode import ExecutionMode
from app.core.errors import MLError, PartialExecutionTrigger

logger = logging.getLogger(__name__)


def run(input_data: dict, context: dict, execution_mode: str) -> tuple:
    trace_id = context.get("trace_id", "unknown")

    current_mode = execution_mode

    if current_mode == ExecutionMode.FULL:
        try:
            logger.info(f"[Trace: {trace_id}] Clustering FULL")
            return {"clusters": [1, 2, 1, 3, 2]}, ExecutionMode.FULL

        except (MLError, PartialExecutionTrigger):
            current_mode = ExecutionMode.PARTIAL

    if current_mode == ExecutionMode.PARTIAL:
        try:
            logger.info(f"[Trace: {trace_id}] Clustering PARTIAL")
            return {"clusters": [1, 1, 1, 1], "partial": True}, ExecutionMode.PARTIAL

        except Exception:
            current_mode = ExecutionMode.FALLBACK

    logger.info(f"[Trace: {trace_id}] Clustering FALLBACK")

    return {
        "clusters": [],
        "fallback": True,
        "confidence": 0.0
    }, ExecutionMode.FALLBACK