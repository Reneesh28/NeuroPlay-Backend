import logging
from app.core.errors import MLError, PartialExecutionTrigger

logger = logging.getLogger(__name__)

def run(input_data: dict, context: dict, target_mode: str) -> tuple:
    """
    Standardized Video Processor with Internal Fallback.
    Rule: NEVER re-run externally; handle mode transitions internally.
    """
    domain = context.get("domain", "unknown")
    trace_id = context.get("trace_id", "unknown")
    
    current_mode = target_mode
    
    # --- PHASE 1: FULL ML ---
    if current_mode == "FULL":
        try:
            logger.info(f"[Trace: {trace_id}] VideoProcessor: Executing FULL mode")
            # Simulate ML Logic
            return {
                "processed": True,
                "domain": domain,
                "frames_analyzed": 120,
                "objects_detected": ["person", "car"]
            }, "FULL"
        except (MLError, PartialExecutionTrigger) as e:
            logger.warning(f"[Trace: {trace_id}] FULL mode failed, downgrading internally: {str(e)}")
            current_mode = "PARTIAL"
        except Exception as e:
            logger.error(f"[Trace: {trace_id}] Critical failure in FULL mode: {str(e)}")
            current_mode = "FALLBACK"

    # --- PHASE 2: PARTIAL ML ---
    if current_mode == "PARTIAL":
        try:
            logger.info(f"[Trace: {trace_id}] VideoProcessor: Executing PARTIAL mode")
            return {
                "processed": True,
                "domain": domain,
                "frames_analyzed": 30,
                "partial": True
            }, "PARTIAL"
        except Exception as e:
            logger.error(f"[Trace: {trace_id}] PARTIAL mode failed: {str(e)}")
            current_mode = "FALLBACK"

    # --- PHASE 3: FALLBACK (HEURISTIC) ---
    logger.info(f"[Trace: {trace_id}] VideoProcessor: Executing FALLBACK mode")
    return {
        "processed": False,
        "domain": domain,
        "fallback": True,
        "status": "fallback",
        "confidence": 0.0,
        "reason": "ml_degradation"
    }, "FALLBACK"