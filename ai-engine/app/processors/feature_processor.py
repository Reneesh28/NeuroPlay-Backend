import logging
from app.core.errors import MLError, PartialExecutionTrigger
from app.core.execution_mode import ExecutionMode

logger = logging.getLogger(__name__)


def run(input_data: dict, context: dict, execution_mode: str) -> tuple:
    trace_id = context.get("trace_id", "unknown")

    current_mode = execution_mode

    if current_mode == ExecutionMode.FULL:
        try:
            logger.info(f"[Trace: {trace_id}] Feature FULL")
            return {"features": [0.12, 0.45, 0.88, 0.23, 0.67]}, ExecutionMode.FULL

        except (MLError, PartialExecutionTrigger):
            current_mode = ExecutionMode.PARTIAL

    if current_mode == ExecutionMode.PARTIAL:
        try:
            logger.info(f"[Trace: {trace_id}] Feature PARTIAL")
            return {"features": [0.1, 0.4, 0.8], "partial": True}, ExecutionMode.PARTIAL

        except Exception:
            current_mode = ExecutionMode.FALLBACK

    logger.info(f"[Trace: {trace_id}] Feature FALLBACK")

    return {
        "features": [0.0, 0.0, 0.0],
        "fallback": True,
        "confidence": 0.0
    }, ExecutionMode.FALLBACK