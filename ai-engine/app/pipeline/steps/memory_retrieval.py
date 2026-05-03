import logging
from typing import Dict, Any

from app.core.execution_mode import ExecutionMode
from services.ml.v2.inference_engine import InferenceEngine

logger = logging.getLogger(__name__)


def run(input_data: Dict[str, Any], context: Dict[str, Any], execution_mode: str):
    trace_id = context.get("trace_id", "unknown")
    domain = context.get("domain") or "blackops"

    try:
        logger.info(f"[Trace: {trace_id}] Memory retrieval FULL | Domain: {domain}")

        raw_data = input_data.get("input_data") or input_data.get("data") or input_data
        embedding = raw_data.get("embedding")

        if not embedding:
            raise ValueError("Missing embedding")

        # 🔥 Initialize engine
        engine = InferenceEngine(domain)

        # 🔥 Use proper search method
        results = engine.search_by_embedding(embedding)

        return {
            "memory": results,
            "embedding": embedding
        }, ExecutionMode.FULL

    except Exception as e:
        logger.exception(f"[Trace: {trace_id}] Memory retrieval failed: {str(e)}")

        return {
            "memory": [],
            "fallback": True
        }, ExecutionMode.FALLBACK