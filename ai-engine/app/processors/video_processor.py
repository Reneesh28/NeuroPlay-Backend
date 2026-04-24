import logging
from app.core.errors import MLError, PartialExecutionTrigger
from app.core.execution_mode import ExecutionMode

logger = logging.getLogger(__name__)


def run(input_data: dict, context: dict, execution_mode: str) -> tuple:
    domain = context.get("domain", "unknown")
    trace_id = context.get("trace_id", "unknown")

    current_mode = execution_mode

    # FULL
    if current_mode == ExecutionMode.FULL:
        try:
            logger.info(f"[Trace: {trace_id}] VideoProcessor FULL")
            return {
                "processed": True,
                "domain": domain,
                "frames_analyzed": 120,
                "objects_detected": ["person", "car"]
            }, ExecutionMode.FULL

        except (MLError, PartialExecutionTrigger):
            logger.warning(f"[Trace: {trace_id}] FULL → PARTIAL")
            current_mode = ExecutionMode.PARTIAL

        except Exception as e:
            logger.error(f"[Trace: {trace_id}] FULL critical: {str(e)}")
            current_mode = ExecutionMode.FALLBACK

    # PARTIAL
    if current_mode == ExecutionMode.PARTIAL:
        try:
            logger.info(f"[Trace: {trace_id}] VideoProcessor PARTIAL")
            return {
                "processed": True,
                "domain": domain,
                "frames_analyzed": 30,
                "partial": True
            }, ExecutionMode.PARTIAL

        except Exception:
            current_mode = ExecutionMode.FALLBACK

    # FALLBACK (must always succeed)
    logger.info(f"[Trace: {trace_id}] VideoProcessor FALLBACK")

    return {
        "processed": False,
        "domain": domain,
        "fallback": True,
        "status": "fallback",
        "confidence": 0.0,
        "reason": "ml_degradation"
    }, ExecutionMode.FALLBACK