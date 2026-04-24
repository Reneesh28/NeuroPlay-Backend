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
    Standardized Wrapper for Monotonic Downgrade Execution.
    Rule: NEVER re-run externally; call processor ONCE and let it handle transitions.
    """
    trace_id = context.get("trace_id", "unknown")
    
    try:
        # Call processor ONCE starting in FULL mode
        # The processor is responsible for internal monotonic downgrades
        result, actual_mode = processor_func(input_data, context, ExecutionMode.FULL)
        
        if actual_mode != ExecutionMode.FULL:
            logger.warning(f"[Trace: {trace_id}] Execution downgraded internally to {actual_mode}")
            
        return result, actual_mode
        
    except Exception as e:
        # Emergency catch-all for catastrophic processor failure
        logger.critical(f"[Trace: {trace_id}] CATASTROPHIC PROCESSOR FAILURE: {str(e)}")
        logger.error(traceback.format_exc())
        
        return {
            "output": {},
            "status": "fallback",
            "confidence": 0.0,
            "reason": "critical_failure",
            "message": f"Critical failure in all execution modes: {str(e)}"
        }, ExecutionMode.FALLBACK
