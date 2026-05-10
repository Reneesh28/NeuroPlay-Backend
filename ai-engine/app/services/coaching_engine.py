"""
Coaching Engine — Phase 8: Persistent Digital Twin

Generates personalized coaching recommendations based on:
- Long-term trends (from trend_engine)
- Player profile identity (from profile_schema)
- Tactical weaknesses (from pattern_extractor)
- Recent simulation failures

RULES:
- All coaching is DATA-GROUNDED. No fabricated statistics.
- Templates are filled with real values from the profile/trends.
- Returns a prioritized list of coaching messages.
- Maximum 5 coaching messages per call.
- NEVER crashes — returns generic safe advice on error.
"""

import logging
from typing import Dict, Any, List, Optional

from app.prompting.coaching_templates import (
    AGGRESSION_TEMPLATES,
    ADAPTABILITY_TEMPLATES,
    CONFIDENCE_TEMPLATES,
    PATTERN_TEMPLATES,
    WEAKNESS_TEMPLATES
)

logger = logging.getLogger(__name__)

# === CONFIGURATION ===
MAX_COACHING_MESSAGES = 5

# Cluster style suggestions for diversity coaching
STYLE_SUGGESTIONS = {
    "aggressive": "defensive or flanking",
    "defensive": "aggressive or flanking",
    "flanking": "anchoring or support",
    "anchoring": "transition or flanking",
    "sniping": "rush or entry",
    "support": "aggressive or flanking",
    "transition": "anchoring or defensive",
    "rush": "sniping or defensive",
    "unknown": "varied tactical"
}


def generate_coaching(
    profile: Optional[Dict[str, Any]] = None,
    trends: Optional[Dict[str, Any]] = None,
    patterns: Optional[Dict[str, Any]] = None,
    recent_output: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Main entry point: generates personalized coaching messages.

    Args:
        profile:        Player profile summary dict.
        trends:         Trend analysis results from trend_engine.
        patterns:       Pattern extraction results from pattern_extractor.
        recent_output:  Most recent simulation output (optional).

    Returns:
        List of coaching messages, each:
        {
            "category": str,
            "priority": int,  (1 = highest)
            "message": str
        }
        Sorted by priority (ascending = most important first).
        Bounded to MAX_COACHING_MESSAGES.
    """
    try:
        messages = []

        # === 1. AGGRESSION COACHING ===
        if profile:
            aggression_msgs = _generate_aggression_coaching(profile)
            messages.extend(aggression_msgs)

        # === 2. ADAPTABILITY COACHING ===
        if profile:
            adaptability_msgs = _generate_adaptability_coaching(profile, trends)
            messages.extend(adaptability_msgs)

        # === 3. CONFIDENCE COACHING ===
        if trends:
            confidence_msgs = _generate_confidence_coaching(trends, profile)
            messages.extend(confidence_msgs)

        # === 4. PATTERN-BASED COACHING ===
        if patterns:
            pattern_msgs = _generate_pattern_coaching(patterns)
            messages.extend(pattern_msgs)

        # === 5. WEAKNESS-BASED COACHING ===
        if patterns and patterns.get("weaknesses"):
            weakness_msgs = _generate_weakness_coaching(patterns)
            messages.extend(weakness_msgs)

        # Sort by priority (lower = more important)
        messages.sort(key=lambda x: x.get("priority", 99))

        # Bound output
        result = messages[:MAX_COACHING_MESSAGES]

        if not result:
            result = [_default_coaching()]

        logger.info(
            f"[CoachingEngine] Generated {len(result)} coaching messages | "
            f"Top: {result[0].get('category', 'N/A') if result else 'none'}"
        )

        return result

    except Exception as e:
        logger.error(f"[CoachingEngine] Error: {str(e)}")
        return [_default_coaching()]


def _generate_aggression_coaching(profile: Dict) -> List[Dict]:
    """Generate aggression-related coaching."""
    messages = []
    aggression = float(profile.get("aggression_score", 0.5))

    if aggression > 0.75:
        template = AGGRESSION_TEMPLATES["too_aggressive"]
        msg = template["template"].format(pct_aggressive=aggression)
        messages.append({
            "category": "aggression",
            "priority": template["priority"],
            "message": msg
        })
    elif aggression < 0.3:
        template = AGGRESSION_TEMPLATES["too_passive"]
        msg = template["template"].format(pct_defensive=1 - aggression)
        messages.append({
            "category": "aggression",
            "priority": template["priority"],
            "message": msg
        })
    elif 0.4 <= aggression <= 0.6:
        template = AGGRESSION_TEMPLATES["balanced"]
        msg = template["template"].format(aggression_score=aggression)
        messages.append({
            "category": "aggression",
            "priority": template["priority"],
            "message": msg
        })

    return messages


def _generate_adaptability_coaching(
    profile: Dict,
    trends: Optional[Dict] = None
) -> List[Dict]:
    """Generate adaptability-related coaching."""
    messages = []
    adaptability = float(profile.get("adaptability_score", 0.5))
    preferred_style = profile.get("preferred_style", "unknown")
    cluster_dist = profile.get("cluster_distribution", {})

    if adaptability < 0.35:
        total = sum(cluster_dist.values()) if cluster_dist else 1
        dominant_count = max(cluster_dist.values()) if cluster_dist else 0
        dominant_pct = dominant_count / total if total > 0 else 0

        suggested = STYLE_SUGGESTIONS.get(preferred_style, "varied tactical")

        template = ADAPTABILITY_TEMPLATES["low_diversity"]
        msg = template["template"].format(
            dominant_style=preferred_style,
            dominant_pct=dominant_pct,
            suggested_style=suggested
        )
        messages.append({
            "category": "adaptability",
            "priority": template["priority"],
            "message": msg
        })
    elif adaptability > 0.7:
        unique_clusters = len([v for v in cluster_dist.values() if v > 0])
        diversity = trends.get("tactical_diversity", adaptability) if trends else adaptability

        template = ADAPTABILITY_TEMPLATES["high_diversity"]
        msg = template["template"].format(
            diversity=diversity,
            unique_clusters=unique_clusters
        )
        messages.append({
            "category": "adaptability",
            "priority": template["priority"],
            "message": msg
        })

    return messages


def _generate_confidence_coaching(
    trends: Dict,
    profile: Optional[Dict] = None
) -> List[Dict]:
    """Generate confidence trend coaching."""
    messages = []
    survival_trend = float(trends.get("survival_trend", 0.0))
    total_sims = int(profile.get("total_simulations", 0)) if profile else 0
    window = min(total_sims, 25)

    if survival_trend < -0.2:
        template = CONFIDENCE_TEMPLATES["declining"]
        msg = template["template"].format(
            confidence_drop=abs(survival_trend),
            window=window
        )
        messages.append({
            "category": "confidence",
            "priority": template["priority"],
            "message": msg
        })
    elif survival_trend > 0.2:
        template = CONFIDENCE_TEMPLATES["improving"]
        msg = template["template"].format(
            confidence_gain=survival_trend,
            window=window
        )
        messages.append({
            "category": "confidence",
            "priority": template["priority"],
            "message": msg
        })

    return messages


def _generate_pattern_coaching(patterns: Dict) -> List[Dict]:
    """Generate coaching from extracted patterns."""
    messages = []
    pattern_list = patterns.get("patterns", [])

    for pattern in pattern_list[:3]:  # Max 3 pattern-based messages
        ptype = pattern.get("type", "other")
        template = PATTERN_TEMPLATES.get(ptype)

        if template:
            msg = pattern.get("description", "")
            if msg:
                messages.append({
                    "category": "patterns",
                    "priority": template["priority"],
                    "message": msg
                })

    return messages


def _generate_weakness_coaching(patterns: Dict) -> List[Dict]:
    """Generate coaching from identified weaknesses."""
    messages = []
    weaknesses = patterns.get("weaknesses", [])

    for weakness in weaknesses[:2]:  # Max 2 weakness-based messages
        messages.append({
            "category": "weakness",
            "priority": 2,
            "message": weakness
        })

    return messages


def _default_coaching() -> Dict[str, Any]:
    """Safe fallback coaching message."""
    return {
        "category": "general",
        "priority": 5,
        "message": "Focus on fundamentals: crosshair placement, utility usage, and communication."
    }


def get_top_coaching_tip(
    profile: Optional[Dict] = None,
    trends: Optional[Dict] = None,
    patterns: Optional[Dict] = None
) -> str:
    """
    Convenience function: returns the single most important coaching tip.
    Used by the simulation step for inline coaching.
    """
    messages = generate_coaching(profile, trends, patterns)
    if messages:
        return messages[0].get("message", "Stay aware and adapt to the situation.")
    return "Stay aware and adapt to the situation."
