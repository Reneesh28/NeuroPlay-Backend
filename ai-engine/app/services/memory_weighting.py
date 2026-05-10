"""
Memory Weighting System — Phase 8: Persistent Digital Twin

Enhances raw FAISS similarity retrieval with multi-factor weighted scoring.

Scoring Factors:
1. FAISS similarity distance (lower = better)
2. Recency (newer memories score higher)
3. Confidence (higher ML confidence = more reliable)
4. Outcome success (successful outcomes weighted higher)
5. Cluster stability (consistent cluster = more trustworthy)

RULES:
- Input: raw memory results from memory_retrieval step.
- Output: ranked and filtered memory list.
- NEVER crashes — returns empty list on error.
- Deterministic for the same input (no randomness).
- Filters out noisy memories below quality threshold.
"""

import logging
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# === WEIGHT CONFIGURATION ===
WEIGHT_SIMILARITY = 0.35       # FAISS distance weight
WEIGHT_RECENCY = 0.25          # Time decay weight
WEIGHT_CONFIDENCE = 0.20       # ML confidence weight
WEIGHT_OUTCOME = 0.10          # Historical outcome weight
WEIGHT_CLUSTER_STABILITY = 0.10  # Cluster consistency weight

# === THRESHOLDS ===
MIN_COMPOSITE_SCORE = 0.15     # Minimum score to keep a memory
MAX_WEIGHTED_MEMORIES = 10     # Maximum memories after weighting

# === RECENCY PARAMETERS ===
RECENCY_HALF_LIFE = 50         # Memories lose 50% weight after N entries
MAX_DISTANCE = 5.0             # Maximum acceptable FAISS distance


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp value to [low, high]."""
    return max(low, min(high, value))


def _distance_to_similarity(distance: float) -> float:
    """
    Converts FAISS L2 distance to a similarity score [0, 1].
    Lower distance → higher similarity.
    """
    if distance <= 0:
        return 1.0
    if distance >= MAX_DISTANCE:
        return 0.0

    return _clamp(1.0 - (distance / MAX_DISTANCE))


def _recency_score(index: int, total: int) -> float:
    """
    Computes a recency score based on position in the list.
    First entry (most recent) gets highest score.

    Uses exponential decay: score = 2^(-index / half_life)
    """
    if total <= 1:
        return 1.0

    decay = 2.0 ** (-index / RECENCY_HALF_LIFE)
    return _clamp(decay)


def _confidence_score(confidence: float) -> float:
    """Normalizes ML confidence to a weight factor."""
    return _clamp(float(confidence) if confidence else 0.0)


def _outcome_score(memory: dict) -> float:
    """
    Derives an outcome success signal from memory metadata.
    If the memory led to a positive outcome (e.g., survival, kill),
    it gets a higher weight.
    """
    # Check for explicit outcome field
    outcome = memory.get("outcome")
    if outcome is not None:
        if isinstance(outcome, (int, float)):
            return _clamp(float(outcome))
        if isinstance(outcome, str):
            positive_outcomes = {"success", "survived", "kill", "win", "positive"}
            return 0.8 if outcome.lower() in positive_outcomes else 0.3

    # Fallback: infer from confidence
    confidence = float(memory.get("confidence", 0.5))
    return _clamp(confidence * 0.8)


def _cluster_stability_score(
    memory: dict,
    cluster_distribution: Optional[Dict[str, int]] = None
) -> float:
    """
    Computes cluster stability: memories from frequently-visited clusters
    are more trustworthy.
    """
    if not cluster_distribution:
        return 0.5

    cluster_id = memory.get("cluster_id")
    if cluster_id is None:
        return 0.5

    cluster_key = str(cluster_id)
    count = cluster_distribution.get(cluster_key, 0)
    total = sum(cluster_distribution.values()) or 1

    # Proportion of total visits to this cluster
    proportion = count / total
    return _clamp(proportion * 2)  # Scale up: 50%+ of visits = 1.0


def score_memory(
    memory: dict,
    index: int,
    total: int,
    cluster_distribution: Optional[Dict[str, int]] = None
) -> float:
    """
    Computes composite weighted score for a single memory.
    """
    try:
        sim = _distance_to_similarity(float(memory.get("distance", MAX_DISTANCE)))
        rec = _recency_score(index, total)
        conf = _confidence_score(memory.get("confidence", 0.0))
        out = _outcome_score(memory)
        stab = _cluster_stability_score(memory, cluster_distribution)

        composite = (
            WEIGHT_SIMILARITY * sim +
            WEIGHT_RECENCY * rec +
            WEIGHT_CONFIDENCE * conf +
            WEIGHT_OUTCOME * out +
            WEIGHT_CLUSTER_STABILITY * stab
        )

        return round(_clamp(composite), 4)

    except Exception:
        return 0.0


def rank_memories(
    memories: List[Dict[str, Any]],
    cluster_distribution: Optional[Dict[str, int]] = None
) -> List[Dict[str, Any]]:
    """
    Main entry point: ranks and filters memories by composite score.

    Args:
        memories:             Raw memory results from FAISS retrieval.
        cluster_distribution: Player's cluster distribution (from profile).

    Returns:
        Ranked list of memories with composite_score attached.
        Filtered to remove entries below MIN_COMPOSITE_SCORE.
        Bounded to MAX_WEIGHTED_MEMORIES.
    """
    if not memories or not isinstance(memories, list):
        return []

    try:
        total = len(memories)
        scored = []

        for i, mem in enumerate(memories):
            if not isinstance(mem, dict):
                continue

            composite = score_memory(mem, i, total, cluster_distribution)

            if composite >= MIN_COMPOSITE_SCORE:
                enriched = {**mem, "composite_score": composite}
                scored.append(enriched)

        # Sort by composite score (descending)
        scored.sort(key=lambda x: x.get("composite_score", 0), reverse=True)

        # Bound output
        result = scored[:MAX_WEIGHTED_MEMORIES]

        logger.info(
            f"[MemoryWeighting] Input: {total} | "
            f"Passed filter: {len(scored)} | "
            f"Returned: {len(result)} | "
            f"Top score: {result[0].get('composite_score', 0) if result else 'N/A'}"
        )

        return result

    except Exception as e:
        logger.error(f"[MemoryWeighting] Error: {str(e)}")
        return []
