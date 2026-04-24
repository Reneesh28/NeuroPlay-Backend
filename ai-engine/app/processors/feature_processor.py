import logging

logger = logging.getLogger(__name__)

def run(input_data: dict, context: dict, execution_mode: str) -> dict:
    """
    Standardized Feature Processor.
    """
    domain = context.get("domain", "unknown")
    trace_id = context.get("trace_id", "unknown")
    
    logger.info(f"[Trace: {trace_id}] Extracting features for domain {domain} in {execution_mode} mode")
    
    if execution_mode == "FULL":
        features = [0.12, 0.45, 0.88, 0.23, 0.67]
    elif execution_mode == "PARTIAL":
        features = [0.1, 0.4, 0.8]
    else:
        features = [0.0, 0.0, 0.0]
        
    return {
        "features": features,
        "execution_mode": execution_mode,
        "domain": domain
    }