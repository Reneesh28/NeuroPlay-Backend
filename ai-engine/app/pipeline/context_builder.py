"""
Context Builder — Phase 7: Digital Twin Reasoning Layer

Aggregates current game state, memory retrieval results, and cluster
patterns into a structured reasoning context that the LLM can consume
deterministically.

IMPORTANT:
- This module does NOT call the LLM.
- It only prepares the context payload.
- All fields are bounded and sanitized.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# ==============================
# CLUSTER → TACTICAL LABEL MAP
# ==============================
CLUSTER_LABELS = {
    0: "Defensive / Passive",
    1: "Aggressive / Push",
    2: "Flanking / Rotational",
    3: "Holding / Anchoring",
    4: "Sniping / Long Range",
    5: "Utility / Support",
    6: "Transition / Repositioning",
    7: "Rush / Entry"
}

# Max memories to inject into context (token budget control)
MAX_MEMORY_ENTRIES = 5
MAX_EVENT_ENTRIES = 10


def _extract_current_state(input_data: dict) -> dict:
    """
    Extracts and normalizes the current game state from raw input_data.

    The input_data may come in different shapes depending on which
    pipeline step produced it. We normalize to a flat state dict.
    """
    raw = input_data.get("input_data") or input_data.get("data") or input_data

    if isinstance(raw, dict):
        player_state = raw.get("player_state", {})
        events = raw.get("events", [])
    else:
        player_state = {}
        events = []

    # Bound events to prevent payload bloat
    if len(events) > MAX_EVENT_ENTRIES:
        events = events[:MAX_EVENT_ENTRIES]

    return {
        "player_state": player_state,
        "events": events
    }


def _summarize_memory(memory_results: list) -> List[dict]:
    """
    Converts raw memory retrieval results into a compact summary
    suitable for LLM consumption.

    Each memory entry contains:
    - cluster_id → mapped to a tactical label
    - confidence → ML confidence score
    - distance → similarity distance from FAISS
    - player_state → historical state snapshot
    - events → what happened in that historical segment
    """
    if not memory_results or not isinstance(memory_results, list):
        return []

    summarized = []

    for entry in memory_results[:MAX_MEMORY_ENTRIES]:
        if not isinstance(entry, dict):
            continue

        cluster_id = entry.get("cluster_id", -1)
        tactical_label = CLUSTER_LABELS.get(cluster_id, "Unknown Pattern")

        summarized.append({
            "tactical_pattern": tactical_label,
            "cluster_id": cluster_id,
            "similarity_confidence": round(float(entry.get("confidence", 0.0)), 3),
            "distance": round(float(entry.get("distance", 999.0)), 3),
            "historical_state": entry.get("player_state", {}),
            "historical_events": entry.get("events", [])[:5]  # cap events per memory
        })

    return summarized


def _extract_patterns(memory_summary: list) -> dict:
    """
    Derives macro-level tactical patterns from the memory summary.

    This gives the LLM a high-level overview of what patterns dominate
    the player's recent history, without needing to parse each memory.
    """
    if not memory_summary:
        return {
            "dominant_pattern": "Unknown",
            "pattern_distribution": {},
            "avg_confidence": 0.0
        }

    pattern_counts = {}
    total_confidence = 0.0

    for entry in memory_summary:
        label = entry.get("tactical_pattern", "Unknown")
        pattern_counts[label] = pattern_counts.get(label, 0) + 1
        total_confidence += entry.get("similarity_confidence", 0.0)

    # Find dominant pattern
    dominant = max(pattern_counts, key=pattern_counts.get) if pattern_counts else "Unknown"

    avg_confidence = total_confidence / len(memory_summary) if memory_summary else 0.0

    return {
        "dominant_pattern": dominant,
        "pattern_distribution": pattern_counts,
        "avg_confidence": round(avg_confidence, 3)
    }


def build_reasoning_context(
    input_data: dict,
    context: dict,
    memory_data: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Main entry point: builds the full reasoning context.

    Args:
        input_data:   Raw pipeline input (from loader / previous step output)
        context:      Execution context (user_id, session_id, domain, trace_id, etc.)
        memory_data:  Output from memory_retrieval step (optional, may be None if FALLBACK)

    Returns:
        Structured dict ready for prompt injection:
        {
            "current_state": { player_state, events },
            "memory": [ { tactical_pattern, cluster_id, ... }, ... ],
            "patterns": { dominant_pattern, pattern_distribution, avg_confidence },
            "cluster": { ... },
            "meta": { domain, trace_id }
        }
    """
    trace_id = context.get("trace_id", "unknown")

    logger.info(f"[Trace:{trace_id}] Building reasoning context")

    # 1. Current state
    current_state = _extract_current_state(input_data)

    # 2. Memory synthesis
    memory_results = []
    if memory_data and isinstance(memory_data, dict):
        memory_results = memory_data.get("memory", [])

    memory_summary = _summarize_memory(memory_results)

    # 3. Pattern analysis
    patterns = _extract_patterns(memory_summary)

    # 4. Cluster metadata
    cluster_info = {}
    if memory_data and isinstance(memory_data, dict):
        metadata = memory_data.get("metadata", {})
        cluster_info = {
            "raw_matches": metadata.get("raw_count", 0),
            "quality_matches": metadata.get("filtered_count", 0),
            "has_fallback": memory_data.get("fallback", False)
        }

    reasoning_context = {
        "current_state": current_state,
        "memory": memory_summary,
        "patterns": patterns,
        "cluster": cluster_info,
        "meta": {
            "domain": context.get("domain", "unknown"),
            "trace_id": trace_id
        }
    }

    logger.info(
        f"[Trace:{trace_id}] Context built | "
        f"Memories: {len(memory_summary)} | "
        f"Dominant: {patterns.get('dominant_pattern', 'N/A')}"
    )

    return reasoning_context
