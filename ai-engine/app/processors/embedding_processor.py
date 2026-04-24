import logging

logger = logging.getLogger(__name__)

def run(input_data: dict, context: dict, target_mode: str) -> tuple:
    """Standardized Embedding Processor with Internal Fallback."""
    trace_id = context.get("trace_id", "unknown")
    current_mode = target_mode
    
    if current_mode == "FULL":
        try:
            logger.info(f"[Trace: {trace_id}] EmbeddingProcessor: Executing FULL mode")
            return {"embedding": [0.1, 0.2, 0.3, 0.4, 0.5]}, "FULL"
        except Exception:
            current_mode = "PARTIAL"

    if current_mode == "PARTIAL":
        try:
            logger.info(f"[Trace: {trace_id}] EmbeddingProcessor: Executing PARTIAL mode")
            return {"embedding": [0.1, 0.2, 0.3], "partial": True}, "PARTIAL"
        except Exception:
            current_mode = "FALLBACK"

    logger.info(f"[Trace: {trace_id}] EmbeddingProcessor: Executing FALLBACK mode")
    return {"embedding": [0.0], "fallback": True}, "FALLBACK"