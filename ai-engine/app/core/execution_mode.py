import traceback
import logging
from typing import Callable, Any, Tuple, Dict
from app.core.errors import SystemError

logger = logging.getLogger(__name__)


class ExecutionMode:
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    FALLBACK = "FALLBACK"

def run_with_fallback(
    processor_func: Callable,
    input_data: Dict[str, Any],
    context: Dict[str, Any]
) -> Tuple[Dict[str, Any], str]:
    """
    Calls processor ONCE.
    Processor handles internal downgrade.
    """

    trace_id = context.get("trace_id", "unknown")

    try:
        result, actual_mode = processor_func(
            input_data,
            context,
            ExecutionMode.FULL
        )

        if actual_mode != ExecutionMode.FULL:
            logger.warning(f"[Trace: {trace_id}] Downgraded → {actual_mode}")

        return result, actual_mode

    except Exception as e:
        logger.critical(f"[Trace: {trace_id}] CATASTROPHIC FAILURE: {str(e)}")
        logger.error(traceback.format_exc())

        return {
            "output": {},
            "status": "fallback",
            "confidence": 0.0,
            "reason": "critical_failure"
        }, ExecutionMode.FALLBACK