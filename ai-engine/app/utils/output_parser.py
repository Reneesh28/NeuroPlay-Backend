"""
Output Parser — Phase 7: Digital Twin Reasoning Layer

Extracts valid JSON from LLM responses, handling common
LLM artifacts like markdown fences, preamble text, and
malformed brackets.

RULES:
- Always return a valid dict with the expected schema.
- Never raise — always degrade to fallback on failure.
- Log all parse failures for debugging.
"""

import json
import re
import logging

logger = logging.getLogger(__name__)

# Expected output keys
REQUIRED_KEYS = {"predicted_action", "confidence", "reasoning", "coaching_tip"}


def _strip_markdown_fences(text: str) -> str:
    """
    Removes markdown code fences (```json ... ``` or ``` ... ```)
    that LLMs sometimes wrap around JSON output.
    """
    # Remove ```json ... ``` blocks
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    return text.strip()


def _extract_json_block(text: str) -> str:
    """
    Finds the first valid JSON object in the text by locating
    matching { } brackets, handling nested objects.
    """
    start = text.find("{")
    if start == -1:
        return ""

    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]

    # Unbalanced — try with last }
    end = text.rfind("}")
    if end > start:
        return text[start:end + 1]

    return ""


def _normalize_keys(data: dict) -> dict:
    """
    Ensures all expected keys exist in the parsed output.
    Applies type coercion and defaults for missing fields.
    """
    return {
        "predicted_action": str(data.get("predicted_action", "hold position")).strip() or "hold position",
        "confidence": _safe_float(data.get("confidence", 0.5)),
        "reasoning": str(data.get("reasoning", "No reasoning provided")).strip() or "No reasoning provided",
        "coaching_tip": str(data.get("coaching_tip", "Stay aware")).strip() or "Stay aware"
    }


def _safe_float(value, default=0.5) -> float:
    """Safely convert a value to float, returning default on failure."""
    try:
        v = float(value)
        if v != v:  # NaN check
            return default
        return v
    except (ValueError, TypeError):
        return default


def parse_llm_output(text: str) -> dict:
    """
    Main parser: extracts and normalizes JSON from LLM output.

    Parsing strategy (ordered):
    1. Direct json.loads on stripped text
    2. Strip markdown fences, then json.loads
    3. Extract JSON block via bracket matching, then json.loads
    4. Fallback dict

    Returns:
        Always returns a valid dict with all required keys.
    """
    if not text or not isinstance(text, str):
        logger.warning("[Parser] Empty or non-string input → fallback")
        return fallback()

    text = text.strip()

    # --- Attempt 1: Direct parse ---
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            logger.info("[Parser] Direct parse SUCCESS")
            return _normalize_keys(parsed)
    except json.JSONDecodeError:
        pass

    # --- Attempt 2: Strip markdown fences ---
    cleaned = _strip_markdown_fences(text)
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            logger.info("[Parser] Markdown-stripped parse SUCCESS")
            return _normalize_keys(parsed)
    except json.JSONDecodeError:
        pass

    # --- Attempt 3: Extract JSON block ---
    json_block = _extract_json_block(cleaned)
    if json_block:
        try:
            parsed = json.loads(json_block)
            if isinstance(parsed, dict):
                logger.info("[Parser] JSON block extraction SUCCESS")
                return _normalize_keys(parsed)
        except json.JSONDecodeError:
            pass

    # --- Attempt 4: Fallback ---
    logger.warning(f"[Parser] All parse attempts failed | Input preview: {text[:100]}")
    return fallback()


def fallback() -> dict:
    """Returns a safe, pre-validated fallback response."""
    return {
        "predicted_action": "hold position",
        "confidence": 0.5,
        "reasoning": "Parsing failed — applying safe defaults",
        "coaching_tip": "Play safe and gather information"
    }