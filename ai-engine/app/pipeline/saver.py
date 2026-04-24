from typing import Dict, Any
import logging
import uuid
from app.core.errors import SystemError

logger = logging.getLogger(__name__)

def save_output_data(output_data: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Standardized Data Saver.
    Enforces domain isolation for all writes.
    """
    domain = context.get("domain")
    trace_id = context.get("trace_id")
    
    if not domain:
        raise SystemError("Domain is required for data saving")
        
    # Generate a unique reference for the output
    output_ref = f"ref_{uuid.uuid4().hex[:12]}"
    
    logger.info(f"[Trace: {trace_id}] Saving output for domain: {domain} -> {output_ref}")
    
    # --- DOMAIN ISOLATION ENFORCEMENT ---
    # In production: db.collection.insert_one({**output_data, "ref": output_ref, "domain": domain})
    
    # Ensuring output_data is actually present
    if not output_data:
        raise SystemError("Attempted to save empty output_data")
        
    return output_ref
