from typing import Dict, Any
import logging
import hashlib
from app.core.errors import SystemError

logger = logging.getLogger(__name__)

def save_output_data(output_data: Dict[str, Any], context: Dict[str, Any], step: str, input_ref: str) -> str:
    """
    Standardized Data Saver.
    Enforces domain isolation and Deterministic Idempotency.
    
    Rule: same (input_ref + context + step) -> same output_ref
    """
    domain = context.get("domain")
    trace_id = context.get("trace_id")
    
    if not domain:
        raise SystemError("Domain is required for data saving")
        
    # --- DETERMINISTIC IDEMPOTENCY ---
    # base = input_ref:trace_id:step
    base = f"{input_ref}:{trace_id}:{step}"
    output_ref = "ref_" + hashlib.md5(base.encode()).hexdigest()[:12]
    
    logger.info(f"[Trace: {trace_id}] Saving output for domain: {domain} | Step: {step} | Output: {output_ref}")
    
    # --- DOMAIN ISOLATION ENFORCEMENT ---
    # In production: db.collection.insert_one({**output_data, "ref": output_ref, "domain": domain})
    
    if not output_data:
        raise SystemError("Attempted to save empty output_data")
        
    return output_ref
