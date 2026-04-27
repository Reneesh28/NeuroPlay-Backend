from app.core.execution_mode import ExecutionMode


def build_simulation_prompt(input_data, context, mode=ExecutionMode.FULL):

    base = f"""
You are an expert FPS (First Person Shooter) tactical AI coach.

Analyze the situation and return STRICT JSON output.

---

GAME STATE:
{input_data}

PLAYER CONTEXT:
{context}

---
"""

    # 🔹 MODE-SPECIFIC BEHAVIOR
    if mode == ExecutionMode.FULL:
        behavior = """
### EXECUTION MODE: FULL (STRATEGIC ANALYST)
You MUST:
- Think strategically and deeply about the win condition.
- Consider positioning, enemy movement patterns, and calculated risks.
- Provide the OPTIMAL decision for high-level play.
- Use advanced tactical reasoning.
"""

    elif mode == ExecutionMode.PARTIAL:
        behavior = """
### EXECUTION MODE: PARTIAL (CONSERVATIVE ADVISOR)
You MUST:
- Prefer SAFE, low-risk decisions only.
- Avoid aggressive plays or complex maneuvers.
- Keep reasoning simple, direct, and conservative.
- Focus on survival above all else.
"""

    else:
        behavior = """
### EXECUTION MODE: FALLBACK (SAFETY PROTOCOL)
You MUST:
- Return the SAFEST possible action (e.g., hold position, retreat).
- Minimize risk to zero.
- No complex reasoning.
"""

    output_format = """
Return ONLY valid JSON:

{
    "predicted_action": "short action decision",
    "confidence": 0.0,
    "reasoning": "clear explanation",
    "coaching_tip": "practical improvement tip"
}

Rules:
- No extra text or conversational filler.
- No explanation outside JSON.
- Confidence must be between 0 and 1.
"""

    return base + behavior + output_format
