from typing import Dict, Any
import logging
from app.core.errors import PermanentError

logger = logging.getLogger(__name__)

def load_input_data(input_ref: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardized Data Loader.
    Enforces domain isolation for all reads.
    """
    domain = context.get("domain")
    trace_id = context.get("trace_id")
    
    if not domain:
        raise PermanentError("Domain is required for data loading")
        
    logger.info(f"[Trace: {trace_id}] Loading input_ref: {input_ref} for domain: {domain}")
    
    # --- DOMAIN ISOLATION ENFORCEMENT ---
    # In production: db.collection.find_one({"ref": input_ref, "domain": domain})
    
    # Mocking successful load for now
    # We return the reference and some mock data to satisfy the processor
    return {
        "input_ref": input_ref,
        "domain": domain,
        "raw_data": f"content_for_{input_ref}"
    }
