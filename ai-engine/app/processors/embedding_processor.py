import logging

logger = logging.getLogger(__name__)

def run(input_data: dict, context: dict, execution_mode: str) -> dict:
    """
    Standardized Embedding Processor.
    """
    domain = context.get("domain", "unknown")
    trace_id = context.get("trace_id", "unknown")
    
    logger.info(f"[Trace: {trace_id}] Generating embeddings for domain {domain} in {execution_mode} mode")
    
    if execution_mode == "FULL":
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    elif execution_mode == "PARTIAL":
        embedding = [0.1, 0.2, 0.3]
    else:
        embedding = [0.0]
        
    return {
        "embedding": embedding,
        "execution_mode": execution_mode,
        "domain": domain
    }