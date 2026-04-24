from typing import Dict, Any


def _to_float_safe(value, default: float = 0.5) -> float:
    try:
        v = float(value)
        if v != v:  # NaN check
            return default
        return v
    except Exception:
        return default


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def validate_simulation_output(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strict schema guard for simulation output.

    Guarantees:
    - Always returns valid structure
    - Types are correct
    - Values are bounded
    """

    action = raw.get("predicted_action", "hold position")
    if not isinstance(action, str) or not action.strip():
        action = "hold position"

    confidence = _to_float_safe(raw.get("confidence", 0.5), 0.5)
    confidence = _clamp(confidence, 0.0, 1.0)

    reasoning = raw.get("reasoning", "No reasoning provided")
    if not isinstance(reasoning, str):
        reasoning = str(reasoning)

    coaching = raw.get("coaching_tip", "Stay aware")
    if not isinstance(coaching, str):
        coaching = str(coaching)

    return {
        "predicted_action": action,
        "confidence": confidence,
        "reasoning": reasoning,
        "coaching_tip": coaching
    }