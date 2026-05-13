from typing import Dict, Any, Union
import logging
import hashlib
import json
from app.core.errors import SystemError
from app.database.mongo_client import db

logger = logging.getLogger(__name__)


def save_output_data(
    output_data: Dict[str, Any],
    context: Dict[str, Any],
    step: str,
    input_ref: Union[str, Dict[str, Any]]
) -> str:

    domain = context.get("domain")
    trace_id = context.get("trace_id")

    if not domain:
        raise SystemError("Domain is required for data saving")

    # 🔥 FIX: Deterministic output ref handling both string and dict input_ref
    input_ref_str = json.dumps(input_ref, sort_keys=True) if isinstance(input_ref, dict) else str(input_ref)
    
    base = f"{input_ref_str}:{trace_id}:{step}"
    output_ref = "ref_" + hashlib.md5(base.encode()).hexdigest()[:12]

    logger.info(
        f"[Trace: {trace_id}] Saving output | Domain: {domain} | Step: {step} | Output: {output_ref}"
    )

    if not output_data:
        raise SystemError("Attempted to save empty output_data")

    db.segments.update_one(
        {
            "ref": output_ref,
            "domain": domain
        },
        {
            "$set": {
                "ref": output_ref,
                "domain": domain,
                "trace_id": trace_id,
                "step": step,
                "input_ref": input_ref, # Store the actual ref (string or dict)
                "data": output_data
            }
        },
        upsert=True
    )

    return output_ref