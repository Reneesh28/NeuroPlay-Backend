"""
Simulation Output Validator — Phase 7: Digital Twin Reasoning Layer

Strict schema guard for simulation output.

Guarantees:
- Always returns a valid structure with all required fields.
- Types are correct and values are bounded.
- Malformed or missing data is replaced with safe defaults.
- Reasoning and coaching_tip are length-bounded to prevent payload bloat.
"""

from typing import Dict, Any

# ==============================
# SCHEMA CONSTRAINTS
# ==============================
MAX_REASONING_LENGTH = 500
MAX_COACHING_LENGTH = 200
CONFIDENCE_MIN = 0.0
CONFIDENCE_MAX = 1.0

REQUIRED_FIELDS = {"predicted_action", "confidence", "reasoning", "coaching_tip"}


def _to_float_safe(value, default: float = 0.5) -> float:
    """Safe float conversion with NaN protection."""
    try:
        v = float(value)
        if v != v:  # NaN check
            return default
        return v
    except (ValueError, TypeError):
        return default


def _clamp(value: float, low: float, high: float) -> float:
    """Clamps a value between low and high bounds."""
    return max(low, min(high, value))


def _sanitize_string(value, default: str = "", max_length: int = 500) -> str:
    """Ensures a value is a non-empty bounded string."""
    if not isinstance(value, str):
        value = str(value) if value is not None else default

    value = value.strip()

    if not value:
        return default

    if len(value) > max_length:
        return value[:max_length - 3] + "..."

    return value


def validate_simulation_output(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strict schema guard for simulation output.

    Guarantees:
    - Always returns valid structure
    - Types are correct
    - Values are bounded
    - Missing fields are replaced with safe defaults

    Args:
        raw: The parsed LLM output dict.

    Returns:
        Validated and sanitized output dict.
    """
    if not isinstance(raw, dict):
        raw = {}

    # --- predicted_action ---
    action = _sanitize_string(
        raw.get("predicted_action"),
        default="hold position",
        max_length=100
    )

    # --- confidence ---
    confidence = _to_float_safe(raw.get("confidence", 0.5), 0.5)
    confidence = _clamp(confidence, CONFIDENCE_MIN, CONFIDENCE_MAX)

    # --- reasoning ---
    reasoning = _sanitize_string(
        raw.get("reasoning"),
        default="No reasoning provided",
        max_length=MAX_REASONING_LENGTH
    )

    # --- coaching_tip ---
    coaching = _sanitize_string(
        raw.get("coaching_tip"),
        default="Stay aware",
        max_length=MAX_COACHING_LENGTH
    )

    return {
        "predicted_action": action,
        "confidence": confidence,
        "reasoning": reasoning,
        "coaching_tip": coaching
    }