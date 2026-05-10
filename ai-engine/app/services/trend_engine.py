"""
Trend Engine — Phase 8: Persistent Digital Twin

Computes behavioral evolution trends from profile snapshots.

Tracks:
- Survival trend (derived from confidence evolution)
- Aggression trend (slope of aggression_score over time)
- Tactical diversity (cluster distribution entropy)
- Reaction stability (variance of consistency_score)
- Adaptability trend (slope of adaptability_score)

RULES:
- All trends are normalized to [-1.0, 1.0] where:
    - Positive = improving / increasing
    - Negative = declining / decreasing
    - 0 = stable
- Minimum 3 snapshots required for trend computation.
- NEVER crashes — returns neutral trends on error.
"""

import logging
import math
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Minimum snapshots needed to compute a meaningful trend
MIN_SNAPSHOTS_FOR_TREND = 3


def _clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
    """Clamp to trend range."""
    return max(low, min(high, value))


def _compute_slope(values: List[float]) -> float:
    """
    Computes the linear regression slope of a series.
    Normalized to [-1.0, 1.0].

    Uses simple least-squares regression:
    slope = Σ((xi - x̄)(yi - ȳ)) / Σ((xi - x̄)²)
    """
    n = len(values)
    if n < 2:
        return 0.0

    x_mean = (n - 1) / 2.0
    y_mean = sum(values) / n

    numerator = 0.0
    denominator = 0.0

    for i, y in enumerate(values):
        x_diff = i - x_mean
        numerator += x_diff * (y - y_mean)
        denominator += x_diff * x_diff

    if denominator == 0:
        return 0.0

    raw_slope = numerator / denominator

    # Normalize: a slope that would go from 0 to 1 over the window = 1.0
    normalized = raw_slope * n
    return _clamp(normalized)


def _compute_variance(values: List[float]) -> float:
    """Computes variance of a series."""
    if len(values) < 2:
        return 0.0

    mean = sum(values) / len(values)
    return sum((v - mean) ** 2 for v in values) / len(values)


def _compute_entropy(distribution: Dict[str, int]) -> float:
    """
    Computes Shannon entropy of cluster distribution.
    Higher entropy = more diverse tactical behavior.
    """
    if not distribution:
        return 0.0

    total = sum(distribution.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in distribution.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return entropy


def compute_trends(snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Main entry point: computes behavioral trends from snapshots.

    Args:
        snapshots: List of BehaviorSnapshot documents, ordered by created_at ASC.
                   Each snapshot contains:
                   - aggression_score
                   - adaptability_score
                   - avg_confidence
                   - cluster_distribution
                   - consistency_score

    Returns:
        Dict with trend values:
        {
            "survival_trend": float,       # confidence evolution
            "aggression_trend": float,     # aggression direction
            "tactical_diversity": float,   # current entropy (0-1 normalized)
            "reaction_stability": float,   # 1.0 - variance (high = stable)
            "adaptability_trend": float,   # adaptability direction
            "data_quality": str            # "sufficient" or "insufficient"
        }
    """
    try:
        if not snapshots or len(snapshots) < MIN_SNAPSHOTS_FOR_TREND:
            logger.info(
                f"[TrendEngine] Insufficient snapshots: {len(snapshots) if snapshots else 0} "
                f"(need {MIN_SNAPSHOTS_FOR_TREND})"
            )
            return _neutral_trends("insufficient")

        # === EXTRACT SERIES ===
        aggression_series = [
            float(s.get("aggression_score", 0.5)) for s in snapshots
        ]
        adaptability_series = [
            float(s.get("adaptability_score", 0.5)) for s in snapshots
        ]
        confidence_series = [
            float(s.get("avg_confidence", 0.5)) for s in snapshots
        ]
        consistency_series = [
            float(s.get("consistency_score", 0.5)) for s in snapshots
        ]

        # === COMPUTE TRENDS ===
        survival_trend = _compute_slope(confidence_series)
        aggression_trend = _compute_slope(aggression_series)
        adaptability_trend = _compute_slope(adaptability_series)

        # Reaction stability = 1.0 - normalized variance
        consistency_variance = _compute_variance(consistency_series)
        reaction_stability = _clamp(1.0 - (consistency_variance * 4), 0.0, 1.0)

        # Tactical diversity = entropy of latest cluster distribution
        latest_distribution = snapshots[-1].get("cluster_distribution", {})
        raw_entropy = _compute_entropy(latest_distribution)
        # Normalize entropy to [0, 1] (max entropy for 8 clusters = log2(8) = 3.0)
        max_entropy = math.log2(8) if math.log2(8) > 0 else 1.0
        tactical_diversity = _clamp(raw_entropy / max_entropy, 0.0, 1.0)

        trends = {
            "survival_trend": round(survival_trend, 4),
            "aggression_trend": round(aggression_trend, 4),
            "tactical_diversity": round(tactical_diversity, 4),
            "reaction_stability": round(reaction_stability, 4),
            "adaptability_trend": round(adaptability_trend, 4),
            "data_quality": "sufficient"
        }

        logger.info(
            f"[TrendEngine] Trends computed | "
            f"Aggression: {trends['aggression_trend']:+.3f} | "
            f"Survival: {trends['survival_trend']:+.3f} | "
            f"Diversity: {trends['tactical_diversity']:.3f}"
        )

        return trends

    except Exception as e:
        logger.error(f"[TrendEngine] Error computing trends: {str(e)}")
        return _neutral_trends("error")


def _neutral_trends(quality: str = "insufficient") -> Dict[str, Any]:
    """Returns neutral/zero trends as safe default."""
    return {
        "survival_trend": 0.0,
        "aggression_trend": 0.0,
        "tactical_diversity": 0.0,
        "reaction_stability": 0.5,
        "adaptability_trend": 0.0,
        "data_quality": quality
    }
