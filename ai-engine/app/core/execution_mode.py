import traceback
import logging
from typing import Callable, Any, Tuple, Dict
from app.core.errors import TransientError, SystemError, PermanentError, PartialExecutionTrigger, MLError

logger = logging.getLogger(__name__)

class ExecutionMode:
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    FALLBACK = "FALLBACK"

def run_with_fallback(processor_func: Callable, input_data: Dict[str, Any], context: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """
    Executes a processor function with monotonic ML degradation:
    FULL -> PARTIAL -> FALLBACK
    
    Rules:
    - NO retry logic.
    - NEVER re-run same step in different mode if it already succeeded partially.
    - Explicit logging of all downgrade events.
    """
    trace_id = context.get("trace_id", "unknown")
    
    # --- PHASE 1: ATTEMPT FULL ---
    try:
        logger.info(f"[Trace: {trace_id}] Attempting FULL execution mode")
        result = processor_func(input_data, context, ExecutionMode.FULL)
        return result, ExecutionMode.FULL
        
    except (MLError, PartialExecutionTrigger) as e:
        logger.warning(f"[Trace: {trace_id}] FULL mode failed/triggered downgrade. Reason: {str(e)}")
        return _run_partial(processor_func, input_data, context)
        
    except (TransientError, PermanentError):
        # These are NOT handled by fallback logic.
        # Transient = worker retry, Permanent = fail.
        raise
        
    except Exception as e:
        logger.error(f"[Trace: {trace_id}] Unexpected system error in FULL mode: {str(e)}")
        logger.error(traceback.format_exc())
        return _run_fallback(processor_func, input_data, context)

def _run_partial(processor_func: Callable, input_data: Dict[str, Any], context: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """Phase 2: Attempt PARTIAL execution"""
    trace_id = context.get("trace_id", "unknown")
    
    try:
        logger.info(f"[Trace: {trace_id}] Downgrading to PARTIAL execution mode")
        result = processor_func(input_data, context, ExecutionMode.PARTIAL)
        return result, ExecutionMode.PARTIAL
        
    except Exception as e:
        logger.error(f"[Trace: {trace_id}] PARTIAL mode failed: {str(e)}")
        return _run_fallback(processor_func, input_data, context)

def _run_fallback(processor_func: Callable, input_data: Dict[str, Any], context: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """Phase 3: Guaranteed FALLBACK execution"""
    trace_id = context.get("trace_id", "unknown")
    
    logger.error(f"[Trace: {trace_id}] FINAL DOWNGRADE: Executing FALLBACK mode")
    
    try:
        # We still call the processor in FALLBACK mode to ensure structured output
        result = processor_func(input_data, context, ExecutionMode.FALLBACK)
        return result, ExecutionMode.FALLBACK
    except Exception as e:
        # Absolute last resort: Manual emergency fallback structure
        logger.critical(f"[Trace: {trace_id}] FALLBACK MODE CRASHED: {str(e)}")
        return {
            "fallback_emergency": True,
            "status": "degraded",
            "message": "Critical failure in all execution modes"
        }, ExecutionMode.FALLBACK
