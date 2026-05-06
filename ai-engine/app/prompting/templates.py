"""
Prompt Templates — Phase 7: Digital Twin Reasoning Layer

Provides deterministic, mode-aware prompt generation for the simulation LLM.

RULES:
- All prompts enforce STRICT JSON output.
- No free-form conversational responses.
- Mode-specific behavior constraints.
- Context is injected as structured data, NOT raw dicts.
"""

import json
from app.core.execution_mode import ExecutionMode


# ==============================
# SYSTEM PROMPT (PERSONA)
# ==============================
SYSTEM_PROMPT = """You are a Digital Twin — an expert FPS tactical AI reasoning system.

Your role is to analyze the player's current game state, their historical patterns,
and provide a single optimal tactical decision.

HARD RULES:
1. You MUST return ONLY valid JSON. No markdown, no explanation, no extra text.
2. You MUST follow the exact output schema provided.
3. Your reasoning must be step-by-step and grounded in the data provided.
4. If data is incomplete, acknowledge it and give a conservative decision.
5. NEVER fabricate game data that was not provided.

OUTPUT SCHEMA (STRICT):
{
  "predicted_action": "string — the recommended tactical action",
  "confidence": 0.0,
  "reasoning": "string — step-by-step analysis of the situation",
  "coaching_tip": "string — one actionable tip for the player"
}

If you cannot determine the best action, return:
{
  "predicted_action": "hold position",
  "confidence": 0.3,
  "reasoning": "Insufficient data for confident prediction",
  "coaching_tip": "Gather more information before committing"
}"""


# ==============================
# MODE-SPECIFIC BEHAVIOR BLOCKS
# ==============================
MODE_BEHAVIORS = {
    ExecutionMode.FULL: """
EXECUTION MODE: FULL (High Fidelity)

You have access to complete game state and historical memory.

You MUST:
- Think strategically about positioning, timing, and risk
- Consider enemy behavior patterns from historical data
- Provide detailed reasoning (3-5 sentences)
- Recommend optimal actions, including calculated risks
- Reference historical patterns when relevant
- Set confidence between 0.5 and 0.95 based on data quality
""",

    ExecutionMode.PARTIAL: """
EXECUTION MODE: PARTIAL (Degraded)

Some data may be missing or unreliable. Memory retrieval was limited.

You MUST:
- Prefer SAFE, defensive decisions
- Avoid aggressive or risky actions
- Keep reasoning concise (1-3 sentences)
- Focus on survival and positioning
- Set confidence between 0.3 and 0.7
- Do NOT reference historical data if none is provided
""",

    ExecutionMode.FALLBACK: """
EXECUTION MODE: FALLBACK (Minimal)

System is operating in degraded mode. Minimal data available.

You MUST:
- Give the safest possible action
- No aggressive moves
- Set confidence to 0.5
- Keep reasoning to one sentence
"""
}


def _format_context_block(reasoning_context: dict) -> str:
    """
    Formats the structured reasoning context into a readable prompt block.

    Uses JSON serialization for determinism — the LLM sees exactly
    what the system computed, no ambiguity.
    """
    current_state = reasoning_context.get("current_state", {})
    memory = reasoning_context.get("memory", [])
    patterns = reasoning_context.get("patterns", {})
    cluster = reasoning_context.get("cluster", {})

    sections = []

    # --- Current State ---
    sections.append("=== CURRENT GAME STATE ===")
    sections.append(json.dumps(current_state, indent=2, default=str))

    # --- Historical Memory ---
    if memory:
        sections.append("\n=== HISTORICAL MEMORY (Similar Past Situations) ===")
        for i, mem in enumerate(memory, 1):
            sections.append(f"\n--- Memory {i} ---")
            sections.append(f"Pattern: {mem.get('tactical_pattern', 'Unknown')}")
            sections.append(f"Similarity Confidence: {mem.get('similarity_confidence', 0.0)}")
            sections.append(f"Distance: {mem.get('distance', 'N/A')}")
            if mem.get("historical_state"):
                sections.append(f"State: {json.dumps(mem['historical_state'], default=str)}")
            if mem.get("historical_events"):
                sections.append(f"Events: {json.dumps(mem['historical_events'], default=str)}")
    else:
        sections.append("\n=== HISTORICAL MEMORY ===")
        sections.append("No historical data available.")

    # --- Macro Patterns ---
    sections.append("\n=== TACTICAL PATTERN ANALYSIS ===")
    sections.append(f"Dominant Pattern: {patterns.get('dominant_pattern', 'Unknown')}")
    sections.append(f"Pattern Distribution: {json.dumps(patterns.get('pattern_distribution', {}))}")
    sections.append(f"Average Confidence: {patterns.get('avg_confidence', 0.0)}")

    # --- Cluster Info ---
    if cluster:
        sections.append("\n=== CLUSTER METADATA ===")
        sections.append(f"Raw Matches: {cluster.get('raw_matches', 0)}")
        sections.append(f"Quality Matches: {cluster.get('quality_matches', 0)}")

    return "\n".join(sections)


def build_simulation_prompt(
    input_data: dict,
    context: dict,
    mode: str = ExecutionMode.FULL,
    reasoning_context: dict = None
) -> list:
    """
    Builds the full prompt payload for the simulation LLM.

    Args:
        input_data:         Raw pipeline input (legacy support)
        context:            Execution context dict
        mode:               ExecutionMode (FULL / PARTIAL / FALLBACK)
        reasoning_context:  Structured context from ContextBuilder (Phase 7)

    Returns:
        List of message dicts for the chat completion API:
        [
            { "role": "system", "content": "..." },
            { "role": "user", "content": "..." }
        ]
    """
    # --- System message ---
    system_content = SYSTEM_PROMPT

    # --- Behavior block ---
    behavior = MODE_BEHAVIORS.get(mode, MODE_BEHAVIORS[ExecutionMode.FALLBACK])

    # --- Context block ---
    if reasoning_context:
        # Phase 7: Use structured context
        context_block = _format_context_block(reasoning_context)
    else:
        # Legacy fallback: raw injection
        context_block = f"GAME STATE:\n{json.dumps(input_data, indent=2, default=str)}\n\nPLAYER CONTEXT:\n{json.dumps(context, indent=2, default=str)}"

    # --- User message ---
    user_content = f"""{behavior}

{context_block}

RESPOND WITH VALID JSON ONLY. NO MARKDOWN. NO EXPLANATION OUTSIDE THE JSON.
"""

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]