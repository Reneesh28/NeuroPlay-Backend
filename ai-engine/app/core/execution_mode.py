import traceback
import logging
from typing import Callable, Any, Tuple
from app.core.errors import TransientError, SystemError, PermanentError, PartialExecutionTrigger

logger = logging.getLogger(__name__)

class ExecutionMode:
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    FALLBACK = "FALLBACK"

def run_with_fallback(processor_func: Callable, input_ref: str, context: dict) -> Tuple[Any, str]:
    """
    Executes a processor function with graceful ML degradation.
    Returns a tuple of (result, executed_mode).
    """
    try:
        # Attempt FULL execution
        result = processor_func(input_ref, context)
        return result, ExecutionMode.FULL
    except PartialExecutionTrigger:
        logger.warning("Partial ML execution triggered")
        # In a real scenario, the processor might return partial data directly 
        # instead of raising, or we execute a specific partial logic.
        # Simulating partial result here:
        partial_result = _execute_partial(processor_func, input_ref, context)
        return partial_result, ExecutionMode.PARTIAL
    except TransientError as e:
        # Re-raise to allow the queue worker to retry the job
        logger.warning(f"Transient error during ML execution, re-raising for retry: {str(e)}")
        raise
    except PermanentError as e:
        # Re-raise for invalid schema or contract violation (should fail job completely)
        logger.error(f"Permanent error during ML execution, aborting: {str(e)}")
        raise
    except SystemError as e:
        # Internal engine error, downgrade to FALLBACK
        logger.error(f"System error during ML execution, downgrading to FALLBACK: {str(e)}")
        logger.error(traceback.format_exc())
        return _execute_fallback(processor_func, input_ref, context), ExecutionMode.FALLBACK
    except Exception as e:
        # Catch-all for unexpected ML model crashes (e.g., CUDA out of memory, unhandled exceptions)
        logger.error(f"Unexpected ML crash, downgrading to FALLBACK: {str(e)}")
        logger.error(traceback.format_exc())
        return _execute_fallback(processor_func, input_ref, context), ExecutionMode.FALLBACK

def _execute_fallback(processor_func: Callable, input_ref: str, context: dict) -> Any:
    """
    Executes a heuristic or generic fallback logic.
    For now, returns an empty or mock representation to keep the pipeline moving.
    """
    logger.info("Executing fallback heuristic...")
    return {
        "output_ref": f"{input_ref}_fallback",
        "fallback": True,
        "execution_mode": "FALLBACK"
    }

def _execute_partial(processor_func: Callable, input_ref: str, context: dict) -> Any:
    """
    Executes degraded ML pipeline.
    Attempts processor execution, falls back only if needed.
    """
    logger.info("Executing partial ML execution...")

    try:
        result = processor_func(input_ref, context)

        if not isinstance(result, dict) or "output_ref" not in result:
            raise Exception("Invalid partial output")

        result["partial"] = True
        result["execution_mode"] = "PARTIAL"

        return result

    except Exception:
        return {
            "output_ref": f"{input_ref}_partial",
            "partial": True,
            "execution_mode": "PARTIAL"
        }
