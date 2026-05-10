"""
Coaching Templates — Phase 8: Persistent Digital Twin

Template-based coaching message generation grounded in real data.

RULES:
- Every coaching message MUST reference concrete data (percentages, counts, scores).
- No hallucinated statistics — templates only fill in verified values.
- Templates are categorized by coaching topic.
- Each template has a priority level for ranking.
"""


# === TEMPLATE CATEGORIES ===

AGGRESSION_TEMPLATES = {
    "too_aggressive": {
        "priority": 1,
        "template": (
            "{pct_aggressive:.0%} of your deaths occurred during aggressive pushes. "
            "Consider holding angles or using utility before committing to engagements."
        )
    },
    "too_passive": {
        "priority": 2,
        "template": (
            "You chose defensive actions in {pct_defensive:.0%} of encounters. "
            "Opponents may be reading your passivity. Mix in controlled aggression."
        )
    },
    "balanced": {
        "priority": 3,
        "template": (
            "Your aggression balance is {aggression_score:.2f}/1.0 — well-calibrated. "
            "Maintain this and focus on timing your pushes with utility support."
        )
    }
}

ADAPTABILITY_TEMPLATES = {
    "low_diversity": {
        "priority": 1,
        "template": (
            "You predominantly use {dominant_style} tactics ({dominant_pct:.0%}). "
            "Practice {suggested_style} approaches to become less predictable."
        )
    },
    "high_diversity": {
        "priority": 3,
        "template": (
            "Your tactical diversity is {diversity:.2f}/1.0 — excellent. "
            "You use {unique_clusters} different tactical patterns effectively."
        )
    }
}

CONFIDENCE_TEMPLATES = {
    "declining": {
        "priority": 1,
        "template": (
            "Your prediction confidence has dropped {confidence_drop:.0%} over the last "
            "{window} simulations. Focus on fundamentals: crosshair placement and map control."
        )
    },
    "unstable": {
        "priority": 2,
        "template": (
            "Your confidence variance is {variance:.3f} — indicating inconsistent performance. "
            "Develop a pre-round routine to stabilize decision-making."
        )
    },
    "improving": {
        "priority": 3,
        "template": (
            "Confidence is trending upward (+{confidence_gain:.0%}) over the last "
            "{window} simulations. Your practice is paying off."
        )
    }
}

PATTERN_TEMPLATES = {
    "over_reliance": {
        "priority": 1,
        "template": (
            "Pattern detected: you default to {pattern_name} in {frequency} of the last "
            "{total} encounters. This makes you predictable. Consciously vary your approach."
        )
    },
    "tactical_gap": {
        "priority": 2,
        "template": (
            "You have never used {pattern_name} tactics. Adding this to your repertoire "
            "will create new angles and surprise opponents."
        )
    },
    "high_risk_habit": {
        "priority": 1,
        "template": (
            "Warning: {frequency} of your last {total} actions were high-risk plays. "
            "Consider trading risk for positional advantage."
        )
    }
}

WEAKNESS_TEMPLATES = {
    "positioning": {
        "priority": 1,
        "template": (
            "Your positioning is a recurring weakness. {specific_detail} "
            "Practice holding off-angles and pre-aiming common peek spots."
        )
    },
    "timing": {
        "priority": 2,
        "template": (
            "Timing is a key area for improvement. You frequently engage at suboptimal moments. "
            "Wait for utility or teammate support before committing."
        )
    }
}

# === ALL TEMPLATES REGISTRY ===
ALL_TEMPLATES = {
    "aggression": AGGRESSION_TEMPLATES,
    "adaptability": ADAPTABILITY_TEMPLATES,
    "confidence": CONFIDENCE_TEMPLATES,
    "patterns": PATTERN_TEMPLATES,
    "weakness": WEAKNESS_TEMPLATES
}
