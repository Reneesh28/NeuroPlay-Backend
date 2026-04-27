from app.core.execution_mode import ExecutionMode


def build_simulation_prompt(input_data, context, mode=ExecutionMode.FULL):

    base = f"""
You are an expert FPS tactical AI system.

Analyze the situation and return STRICT JSON.

GAME STATE:
{input_data}

PLAYER CONTEXT:
{context}
"""

    if mode == ExecutionMode.FULL:
        behavior = """
You MUST:
- Think strategically
- Consider positioning, risk, and enemy behavior
- Provide optimal decision
- Give detailed reasoning
- You can take calculated risks
"""

    elif mode == ExecutionMode.PARTIAL:
        behavior = """
You MUST:
- Prefer SAFE decisions
- Avoid aggressive or risky actions
- Keep reasoning short and simple
- Focus on survival and positioning
"""

    else:
        behavior = """
You MUST:
- Give safest possible action
- No aggressive moves
"""

    format_block = """
Return ONLY valid JSON.

NO markdown.
NO explanation.
NO extra text.

STRICT RULE:
If output is not valid JSON, the response is invalid.

FORMAT:

{
  "predicted_action": "string",
  "confidence": 0.0,
  "reasoning": "string",
  "coaching_tip": "string"
}
"""

    return base + behavior + format_block