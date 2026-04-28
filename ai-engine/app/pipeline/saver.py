from typing import Dict, Any
import logging
import hashlib
from app.core.errors import SystemError
from app.database.mongo_client import db

logger = logging.getLogger(__name__)


def save_output_data(
    output_data: Dict[str, Any],
    context: Dict[str, Any],
    step: str,
    input_ref: str
) -> str:

    domain = context.get("domain")
    trace_id = context.get("trace_id")

    if not domain:
        raise SystemError("Domain is required for data saving")

    # Deterministic output ref
    base = f"{input_ref}:{trace_id}:{step}"
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
                "input_ref": input_ref,
                "data": output_data
            }
        },
        upsert=True
    )

    return output_ref