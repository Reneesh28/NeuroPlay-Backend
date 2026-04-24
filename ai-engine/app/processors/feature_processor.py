import logging
from app.core.errors import MLError, PartialExecutionTrigger

logger = logging.getLogger(__name__)

def run(input_data: dict, context: dict, target_mode: str) -> tuple:
    """Standardized Feature Processor with Internal Fallback."""
    trace_id = context.get("trace_id", "unknown")
    current_mode = target_mode
    
    if current_mode == "FULL":
        try:
            logger.info(f"[Trace: {trace_id}] FeatureProcessor: Executing FULL mode")
            return {"features": [0.12, 0.45, 0.88, 0.23, 0.67]}, "FULL"
        except Exception:
            current_mode = "PARTIAL"

    if current_mode == "PARTIAL":
        try:
            logger.info(f"[Trace: {trace_id}] FeatureProcessor: Executing PARTIAL mode")
            return {"features": [0.1, 0.4, 0.8], "partial": True}, "PARTIAL"
        except Exception:
            current_mode = "FALLBACK"

    logger.info(f"[Trace: {trace_id}] FeatureProcessor: Executing FALLBACK mode")
    return {"features": [0.0, 0.0, 0.0], "fallback": True}, "FALLBACK"