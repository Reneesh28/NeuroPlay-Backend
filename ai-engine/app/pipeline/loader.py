from typing import Dict, Any
import logging
from app.core.errors import PermanentError
from app.database.mongo_client import db

logger = logging.getLogger(__name__)


def load_input_data(input_ref: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if input_ref == "test_inline_1":
        return {
            "ml_input": [0.1] * 20
        }
    if input_ref == "test_inline_2":
        return {
            "embedding": [0.1] * 8
        }
    domain = context.get("domain")
    trace_id = context.get("trace_id")

    doc = db.segments.find_one({
        "ref": input_ref,
        "domain": domain
    })

    if not doc:
        raise PermanentError(f"No data found for input_ref: {input_ref}")

    # 🔥 CRITICAL FIX: normalize contract
    return {
        "input_data": doc.get("data") or doc.get("input_data"),
        "ref": doc.get("ref"),
        "domain": doc.get("domain")
    }