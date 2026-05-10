"""
Profile Updater — Phase 8: Persistent Digital Twin

Updates the player profile after every simulation based on:
- Simulation output (predicted_action, confidence)
- Memory data (cluster_ids, patterns)
- Execution mode

Uses Exponential Moving Average (EMA) for smooth score evolution.

RULES:
- NEVER crashes — returns the input profile unchanged on error.
- All updates are bounded [0.0, 1.0].
- Idempotent when given the same simulation output.
- Does NOT write to MongoDB directly — returns update payload.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# === EMA ALPHA (controls adaptation speed) ===
EMA_ALPHA = 0.15

# === CLUSTER → STYLE MAPPING ===
CLUSTER_STYLE_MAP = {
    0: "defensive",
    1: "aggressive",
    2: "flanking",
    3: "anchoring",
    4: "sniping",
    5: "support",
    6: "transition",
    7: "rush"
}

# === AGGRESSION-RELATED ACTIONS ===
AGGRESSIVE_ACTIONS = {"push", "rush", "flank", "attack", "engage", "peek", "entry"}
DEFENSIVE_ACTIONS = {"hold position", "retreat", "rotate", "hold", "fall back", "anchor", "defend"}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp a value between low and high."""
    return max(low, min(high, value))


def _ema(current: float, new_value: float, alpha: float = EMA_ALPHA) -> float:
    """Exponential Moving Average update."""
    return _clamp(current * (1 - alpha) + new_value * alpha)


def _compute_aggression_signal(predicted_action: str) -> float:
    """
    Derives an aggression signal [0.0, 1.0] from the predicted action.
    """
    if not predicted_action or not isinstance(predicted_action, str):
        return 0.5

    action_lower = predicted_action.lower().strip()

    for keyword in AGGRESSIVE_ACTIONS:
        if keyword in action_lower:
            return 0.85

    for keyword in DEFENSIVE_ACTIONS:
        if keyword in action_lower:
            return 0.2

    return 0.5  # neutral


def _compute_adaptability_signal(
    cluster_distribution: Dict[str, int],
    new_cluster_id: Optional[int]
) -> float:
    """
    Computes adaptability based on tactical diversity.
    High diversity = high adaptability.
    """
    if not cluster_distribution:
        return 0.5

    total = sum(cluster_distribution.values())
    if total == 0:
        return 0.5

    unique_clusters = len([v for v in cluster_distribution.values() if v > 0])
    max_possible = len(CLUSTER_STYLE_MAP)

    # Diversity ratio
    diversity = unique_clusters / max_possible if max_possible > 0 else 0.5

    return _clamp(diversity)


def _determine_preferred_style(cluster_distribution: Dict[str, int]) -> str:
    """
    Determines the dominant tactical style from cluster distribution.
    """
    if not cluster_distribution:
        return "unknown"

    # Find the cluster with highest frequency
    max_cluster = max(cluster_distribution, key=cluster_distribution.get, default=None)

    if max_cluster is None:
        return "unknown"

    try:
        cluster_id = int(max_cluster)
        return CLUSTER_STYLE_MAP.get(cluster_id, "unknown")
    except (ValueError, TypeError):
        return "unknown"


def compute_profile_update(
    current_profile: Dict[str, Any],
    simulation_output: Dict[str, Any],
    memory_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main entry point: computes the profile update payload.

    Args:
        current_profile:    Current player profile dict (from MongoDB).
        simulation_output:  Output from the simulation step.
        memory_data:        Memory retrieval results (optional).

    Returns:
        Dict of fields to $set on the profile document.
        Does NOT include $inc for version — that's handled by the service.
    """
    try:
        # === EXTRACT CURRENT STATE ===
        current_aggression = float(current_profile.get("aggression_score", 0.5))
        current_adaptability = float(current_profile.get("adaptability_score", 0.5))
        current_distribution = dict(current_profile.get("cluster_distribution", {}))
        total_sims = int(current_profile.get("total_simulations", 0))

        # === EXTRACT SIMULATION OUTPUT ===
        predicted_action = simulation_output.get("predicted_action", "hold position")
        confidence = float(simulation_output.get("confidence", 0.5))

        # === EXTRACT CLUSTER FROM MEMORY ===
        dominant_cluster_id = _extract_dominant_cluster(memory_data)

        # === UPDATE CLUSTER DISTRIBUTION ===
        if dominant_cluster_id is not None:
            cluster_key = str(dominant_cluster_id)
            current_distribution[cluster_key] = current_distribution.get(cluster_key, 0) + 1

        # === COMPUTE NEW SCORES ===
        aggression_signal = _compute_aggression_signal(predicted_action)
        new_aggression = _ema(current_aggression, aggression_signal)

        adaptability_signal = _compute_adaptability_signal(
            current_distribution, dominant_cluster_id
        )
        new_adaptability = _ema(current_adaptability, adaptability_signal)

        # === DETERMINE PREFERRED STYLE ===
        preferred_style = _determine_preferred_style(current_distribution)

        # === BUILD UPDATE PAYLOAD ===
        update_payload = {
            "aggression_score": round(new_aggression, 4),
            "adaptability_score": round(new_adaptability, 4),
            "preferred_style": preferred_style,
            "cluster_distribution": current_distribution,
            "total_simulations": total_sims + 1,
            "last_simulation_at": datetime.utcnow()
        }

        logger.info(
            f"[ProfileUpdater] Update computed | "
            f"Aggression: {current_aggression:.3f} → {new_aggression:.3f} | "
            f"Adaptability: {current_adaptability:.3f} → {new_adaptability:.3f} | "
            f"Style: {preferred_style} | "
            f"Sims: {total_sims + 1}"
        )

        return update_payload

    except Exception as e:
        logger.error(f"[ProfileUpdater] Error computing update: {str(e)}")
        # Return minimal safe update — don't crash the pipeline
        return {
            "total_simulations": int(current_profile.get("total_simulations", 0)) + 1,
            "last_simulation_at": datetime.utcnow()
        }


def _extract_dominant_cluster(memory_data: Optional[Dict[str, Any]]) -> Optional[int]:
    """
    Extracts the dominant cluster_id from memory retrieval data.
    Returns None if no valid cluster found.
    """
    if not memory_data or not isinstance(memory_data, dict):
        return None

    memories = memory_data.get("memory", [])
    if not memories or not isinstance(memories, list):
        return None

    # Count cluster occurrences in memory
    cluster_counts = {}
    for mem in memories:
        if isinstance(mem, dict):
            cid = mem.get("cluster_id")
            if cid is not None:
                cluster_counts[cid] = cluster_counts.get(cid, 0) + 1

    if not cluster_counts:
        return None

    return max(cluster_counts, key=cluster_counts.get)
