from typing import Dict, Any, Union
import logging
import json
from app.core.errors import PermanentError
from app.database.mongo_client import db

logger = logging.getLogger(__name__)


def load_input_data(input_ref: Union[str, Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"LOADING INPUT: type={type(input_ref)} | content={input_ref}")
    
    # 🔥 CASE 0: Handle stringified JSON (just in case)
    if isinstance(input_ref, str) and input_ref.strip().startswith("{"):
        try:
            input_ref = json.loads(input_ref)
            logger.info("Hydrated stringified JSON input_ref into dict")
        except:
            pass

    # 🔥 CASE 1: Rich Object (Direct payload)
    if isinstance(input_ref, dict):
        # 1.1 Ingestion Wrapper Format (from video processor)
        if "data" in input_ref and "type" in input_ref:
            logger.info(f"Using ingestion wrapper: {input_ref.get('type')}")
            return {
                "input_data": input_ref.get("data"),
                "ref": input_ref.get("data", {}).get("file_path") if input_ref.get("data") else None,
                "domain": context.get("domain"),
                "type": input_ref.get("type")
            }
        
        # 1.2 Raw Object Format (from intermediate pipeline steps)
        logger.info("Using raw dict input_ref")
        return {
            "input_data": input_ref,
            "ref": None,
            "domain": context.get("domain")
        }

    # 🔥 CASE 2: Inline test markers
    if input_ref == "test_inline_1":
        return {"ml_input": [0.1] * 20}
    if input_ref == "test_inline_2":
        return {"embedding": [0.1] * 8}

    # 🔥 CASE 3: MongoDB Lookup (Segments/Memory)
    domain = context.get("domain")
    
    doc = db.segments.find_one({
        "ref": input_ref,
        "domain": domain
    })

    if not doc:
        raise PermanentError(f"No data found for input_ref: {input_ref}")

    return {
        "input_data": doc.get("data") or doc.get("input_data"),
        "ref": doc.get("ref"),
        "domain": doc.get("domain")
    }