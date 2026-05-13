import logging
from typing import Dict, Any

from app.core.execution_mode import ExecutionMode
from services.ml.v2.inference_engine import InferenceEngine

logger = logging.getLogger(__name__)

# 🔥 QUALITY GUARDS
MAX_DISTANCE_THRESHOLD = 5.0

def rank_and_filter(results):
    filtered = []
    for r in results:
        dist = r.get("distance", float("inf"))
        if dist <= MAX_DISTANCE_THRESHOLD:
            filtered.append(r)
            
    # Rank by distance (lower is better)
    return sorted(filtered, key=lambda x: x.get("distance", 0))



_engine_cache = {}

def run(input_data: Dict[str, Any], context: Dict[str, Any], execution_mode: str):
    trace_id = context.get("trace_id", "unknown")
    domain = context.get("domain") or "blackops"

    try:
        logger.info(f"[Trace: {trace_id}] Memory retrieval FULL | Domain: {domain}")

        if domain not in _engine_cache:
            _engine_cache[domain] = InferenceEngine(domain)
        
        engine = _engine_cache[domain]

        raw_data = input_data.get("input_data") or input_data.get("data") or input_data
        embedding = raw_data.get("embedding")

        if not embedding:
            raise ValueError("Missing embedding")

        raw_results = engine.search_by_embedding(embedding)

        # 🔥 Apply Quality Guards
        valid_memory = rank_and_filter(raw_results)

        mode = ExecutionMode.FULL
        if not valid_memory:
            logger.warning(f"[Trace: {trace_id}] No memory passed quality threshold. Downgrading to PARTIAL.")
            mode = ExecutionMode.PARTIAL

        return {
            "memory": valid_memory,
            "embedding": embedding,
            "metadata": {
                "raw_count": len(raw_results),
                "filtered_count": len(valid_memory),
                "hit_indices": [int(r.get("faiss_index", 0)) for r in raw_results if "faiss_index" in r]
            }
        }, mode

    except Exception as e:
        logger.exception(f"[Trace: {trace_id}] Memory retrieval failed: {str(e)}")

        return {
            "memory": [],
            "fallback": True
        }, ExecutionMode.FALLBACK