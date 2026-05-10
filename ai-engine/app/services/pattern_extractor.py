"""
Pattern Extractor — Phase 8: Persistent Digital Twin

Discovers recurring tactical patterns from historical data:
- Recurring mistakes
- Tactical strengths
- High-risk habits
- Positioning weaknesses
- Behavioral loops

Uses frequency-based analysis (not ML clustering) to find patterns
that persist across multiple simulations.

RULES:
- Minimum data threshold before generating insights.
- Deduplicates similar patterns.
- Bounded output (max 10 patterns per category).
- NEVER crashes — returns empty insights on error.
"""

import logging
from typing import Dict, Any, List, Optional
from collections import Counter

logger = logging.getLogger(__name__)

# === CONFIGURATION ===
MIN_MEMORIES_FOR_PATTERNS = 5
MAX_PATTERNS_PER_CATEGORY = 10
RECURRING_THRESHOLD = 3  # Minimum occurrences to qualify as a pattern

# === CLUSTER → TACTICAL LABEL MAP ===
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

# === ACTION → RISK CLASSIFICATION ===
HIGH_RISK_ACTIONS = {"push", "rush", "peek", "entry", "engage", "flank"}
LOW_RISK_ACTIONS = {"hold position", "retreat", "rotate", "anchor", "defend"}


def extract_patterns(
    memories: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]] = None,
    confidence_history: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Main entry point: extracts behavioral patterns from historical data.

    Args:
        memories:            List of memory entries (from FAISS retrieval / history).
        profile:             Current player profile (optional, for enrichment).
        confidence_history:  List of recent confidence values (optional).

    Returns:
        {
            "strengths": [str, ...],
            "weaknesses": [str, ...],
            "patterns": [
                {
                    "type": str,
                    "description": str,
                    "frequency": int,
                    "severity": str  # "low", "medium", "high"
                }, ...
            ],
            "data_quality": str  # "sufficient" or "insufficient"
        }
    """
    try:
        if not memories or len(memories) < MIN_MEMORIES_FOR_PATTERNS:
            return _empty_insights("insufficient")

        strengths = []
        weaknesses = []
        patterns = []

        # === 1. CLUSTER FREQUENCY ANALYSIS ===
        cluster_patterns = _analyze_cluster_frequency(memories)
        patterns.extend(cluster_patterns)

        # === 2. ACTION TENDENCY ANALYSIS ===
        action_patterns = _analyze_action_tendencies(memories)
        patterns.extend(action_patterns)

        # === 3. CONFIDENCE TREND ANALYSIS ===
        if confidence_history and len(confidence_history) >= 5:
            confidence_patterns = _analyze_confidence_trends(confidence_history)
            patterns.extend(confidence_patterns)

        # === 4. DERIVE STRENGTHS / WEAKNESSES ===
        strengths = _derive_strengths(memories, profile)
        weaknesses = _derive_weaknesses(memories, profile)

        # === 5. DEDUPLICATE AND BOUND ===
        patterns = _deduplicate_patterns(patterns)[:MAX_PATTERNS_PER_CATEGORY]
        strengths = list(set(strengths))[:MAX_PATTERNS_PER_CATEGORY]
        weaknesses = list(set(weaknesses))[:MAX_PATTERNS_PER_CATEGORY]

        logger.info(
            f"[PatternExtractor] Extracted | "
            f"Strengths: {len(strengths)} | "
            f"Weaknesses: {len(weaknesses)} | "
            f"Patterns: {len(patterns)}"
        )

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "patterns": patterns,
            "data_quality": "sufficient"
        }

    except Exception as e:
        logger.error(f"[PatternExtractor] Error: {str(e)}")
        return _empty_insights("error")


def _analyze_cluster_frequency(memories: List[Dict]) -> List[Dict]:
    """Identifies dominant and neglected tactical clusters."""
    patterns = []
    cluster_counts = Counter()

    for mem in memories:
        cid = mem.get("cluster_id")
        if cid is not None:
            cluster_counts[cid] += 1

    total = sum(cluster_counts.values())
    if total == 0:
        return []

    for cid, count in cluster_counts.most_common():
        label = CLUSTER_LABELS.get(cid, f"Cluster {cid}")
        ratio = count / total

        # Over-reliance on single pattern
        if ratio > 0.4 and count >= RECURRING_THRESHOLD:
            patterns.append({
                "type": "over_reliance",
                "description": f"Over-reliance on {label} pattern ({ratio:.0%} of encounters)",
                "frequency": count,
                "severity": "high" if ratio > 0.6 else "medium"
            })

    # Check for tactical gaps (clusters never used)
    used_clusters = set(cluster_counts.keys())
    for cid, label in CLUSTER_LABELS.items():
        if cid not in used_clusters:
            patterns.append({
                "type": "tactical_gap",
                "description": f"Never uses {label} tactics",
                "frequency": 0,
                "severity": "low"
            })

    return patterns


def _analyze_action_tendencies(memories: List[Dict]) -> List[Dict]:
    """Identifies recurring action patterns and high-risk habits."""
    patterns = []
    action_counts = Counter()

    for mem in memories:
        action = mem.get("predicted_action") or mem.get("action")
        if action and isinstance(action, str):
            action_counts[action.lower().strip()] += 1

    # Find high-risk habits
    high_risk_count = 0
    low_risk_count = 0

    for action, count in action_counts.items():
        for keyword in HIGH_RISK_ACTIONS:
            if keyword in action:
                high_risk_count += count
                break
        for keyword in LOW_RISK_ACTIONS:
            if keyword in action:
                low_risk_count += count
                break

    total_actions = high_risk_count + low_risk_count
    if total_actions > 0 and high_risk_count / total_actions > 0.7:
        patterns.append({
            "type": "high_risk_habit",
            "description": f"Consistently chooses high-risk actions ({high_risk_count}/{total_actions} encounters)",
            "frequency": high_risk_count,
            "severity": "high"
        })
    elif total_actions > 0 and low_risk_count / total_actions > 0.8:
        patterns.append({
            "type": "overly_passive",
            "description": f"Overly passive playstyle ({low_risk_count}/{total_actions} defensive actions)",
            "frequency": low_risk_count,
            "severity": "medium"
        })

    return patterns


def _analyze_confidence_trends(confidence_history: List[float]) -> List[Dict]:
    """Identifies confidence-related patterns."""
    patterns = []

    if len(confidence_history) < 5:
        return []

    recent = confidence_history[-10:]
    avg = sum(recent) / len(recent)

    # Consistently low confidence
    if avg < 0.4:
        patterns.append({
            "type": "low_confidence",
            "description": f"Consistently low prediction confidence (avg: {avg:.2f})",
            "frequency": len(recent),
            "severity": "medium"
        })

    # High variance (unstable)
    variance = sum((c - avg) ** 2 for c in recent) / len(recent)
    if variance > 0.04:
        patterns.append({
            "type": "unstable_confidence",
            "description": f"Highly variable confidence (variance: {variance:.3f})",
            "frequency": len(recent),
            "severity": "medium"
        })

    return patterns


def _derive_strengths(
    memories: List[Dict],
    profile: Optional[Dict]
) -> List[str]:
    """Derives strength labels from patterns."""
    strengths = []

    if profile:
        aggression = float(profile.get("aggression_score", 0.5))
        adaptability = float(profile.get("adaptability_score", 0.5))

        if adaptability > 0.7:
            strengths.append("High tactical adaptability")
        if 0.4 <= aggression <= 0.6:
            strengths.append("Balanced aggression control")

    # Analyze confidence in memories
    high_conf_count = sum(
        1 for m in memories
        if float(m.get("confidence", 0)) > 0.7
    )
    if high_conf_count > len(memories) * 0.6:
        strengths.append("Consistently high-confidence decisions")

    return strengths


def _derive_weaknesses(
    memories: List[Dict],
    profile: Optional[Dict]
) -> List[str]:
    """Derives weakness labels from patterns."""
    weaknesses = []

    if profile:
        aggression = float(profile.get("aggression_score", 0.5))
        adaptability = float(profile.get("adaptability_score", 0.5))

        if aggression > 0.8:
            weaknesses.append("Overly aggressive — high exposure risk")
        if adaptability < 0.3:
            weaknesses.append("Low tactical diversity — predictable to opponents")

    # Low-confidence memories
    low_conf_count = sum(
        1 for m in memories
        if float(m.get("confidence", 1.0)) < 0.4
    )
    if low_conf_count > len(memories) * 0.5:
        weaknesses.append("Frequent low-confidence situations")

    return weaknesses


def _deduplicate_patterns(patterns: List[Dict]) -> List[Dict]:
    """Removes patterns with identical type + description."""
    seen = set()
    unique = []

    for p in patterns:
        key = (p.get("type", ""), p.get("description", ""))
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique


def _empty_insights(quality: str = "insufficient") -> Dict[str, Any]:
    """Returns empty insights as safe default."""
    return {
        "strengths": [],
        "weaknesses": [],
        "patterns": [],
        "data_quality": quality
    }
