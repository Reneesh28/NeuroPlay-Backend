"""
Simulation Step — Phase 7: Digital Twin Reasoning Layer

This is the core simulation pipeline step that:
1. Builds structured reasoning context (Context Builder)
2. Generates mode-aware prompts (Prompt System)
3. Calls the LLM with retry logic (LLM Integration)
4. Parses and validates the output (Output Parser + Validator)
5. Applies confidence calibration (Confidence Control)
6. Returns a deterministic, bounded response

Execution Modes:
- FULL:     ML + Memory + LLM — max confidence 0.95
- PARTIAL:  Degraded memory / LLM conservative — max confidence 0.70
- FALLBACK: No LLM, static safe response — fixed confidence 0.50

RULES:
- NEVER crashes — always returns a valid response.
- ALWAYS returns a tuple: (response_dict, execution_mode).
- Confidence is ALWAYS bounded by mode.
"""

import logging
import json

from app.core.execution_mode import ExecutionMode, detect_ml_failure
from app.models.llm_loader import call_llm
from app.prompting.templates import build_simulation_prompt
from app.utils.output_parser import parse_llm_output
from app.pipeline.validators.simulation_output import validate_simulation_output
from app.pipeline.context_builder import build_reasoning_context
from app.core.response_builder import build_response

logger = logging.getLogger(__name__)


# ==============================
# CONFIDENCE CALIBRATION
# ==============================
CONFIDENCE_CAPS = {
    ExecutionMode.FULL: 0.95,
    ExecutionMode.PARTIAL: 0.70,
    ExecutionMode.FALLBACK: 0.50
}


def calibrate_confidence(confidence, mode):
    """
    Applies mode-specific confidence caps.

    FULL:     max 0.95
    PARTIAL:  max 0.70
    FALLBACK: fixed 0.50
    """
    try:
        confidence = float(confidence)
    except (ValueError, TypeError):
        confidence = 0.5

    if mode == ExecutionMode.FALLBACK:
        return 0.5

    cap = CONFIDENCE_CAPS.get(mode, 0.5)
    return min(confidence, cap)


# ==============================
# STATIC RESPONSES
# ==============================
def fallback_response():
    """Pre-validated static response for FALLBACK mode."""
    return {
        "predicted_action": "hold position",
        "confidence": 0.5,
        "reasoning": "Fallback action applied due to system uncertainty",
        "coaching_tip": "Play safe and gather information"
    }


def partial_response():
    """Pre-validated static response for PARTIAL mode when LLM also fails."""
    return {
        "predicted_action": "hold position",
        "confidence": 0.6,
        "reasoning": "System degraded, applying conservative strategy",
        "coaching_tip": "Focus on safety and positioning"
    }


# ==============================
# MAIN EXECUTION
# ==============================
def run(input_data: dict, context: dict, execution_mode: str) -> tuple:
    """
    Executes the simulation step.

    Flow:
    1. Input validation → fallback if invalid
    2. Pre-triggered fallback check
    3. Build reasoning context (Context Builder)
    4. Generate prompt (Prompt System)
    5. Call LLM (with retry)
    6. Parse output (multi-strategy)
    7. Validate structure (schema guard)
    8. Calibrate confidence (mode-specific cap)
    9. Return response

    Args:
        input_data:      Raw pipeline input (from loader / previous step output)
        context:         Execution context dict (user_id, session_id, domain, trace_id, etc.)
        execution_mode:  Current pipeline execution mode (FULL / PARTIAL / FALLBACK)

    Returns:
        Tuple of (response_dict, execution_mode_str)
    """
    trace_id = context.get("trace_id", "unknown")

    # ==============================
    # 🔥 HARD GUARD: invalid input
    # ==============================
    if not input_data or not isinstance(input_data, dict):
        logger.warning(f"[Trace:{trace_id}] Invalid input_data → fallback")
        return build_response(fallback_response(), ExecutionMode.FALLBACK), ExecutionMode.FALLBACK

    # ==============================
    # PRE-TRIGGERED FALLBACK
    # ==============================
    if execution_mode == ExecutionMode.FALLBACK:
        logger.info(f"[Trace:{trace_id}] MODE: FALLBACK (pre-triggered)")
        return build_response(fallback_response(), ExecutionMode.FALLBACK), ExecutionMode.FALLBACK

    try:
        # ==============================
        # STEP 1: BUILD REASONING CONTEXT
        # ==============================
        memory_data = _extract_memory_data(input_data)

        reasoning_context = build_reasoning_context(
            input_data=input_data,
            context=context,
            memory_data=memory_data
        )

        logger.info(f"[Trace:{trace_id}] CONTEXT BUILT")

        # ==============================
        # STEP 2: GENERATE PROMPT
        # ==============================
        prompt = build_simulation_prompt(
            input_data=input_data,
            context=context,
            mode=execution_mode,
            reasoning_context=reasoning_context
        )

        logger.info(f"[Trace:{trace_id}] PROMPT GENERATED | Mode: {execution_mode}")

        # ==============================
        # STEP 3: LLM CALL
        # ==============================
        raw = call_llm(prompt, temperature=0.4)

        if not raw:
            raise Exception("LLM returned empty response after all retries")

        logger.info(f"[Trace:{trace_id}] LLM RESPONSE RECEIVED")

        # ==============================
        # STEP 4: PARSE OUTPUT
        # ==============================
        parsed = parse_llm_output(raw)

        if not parsed:
            raise Exception("Parsed output empty after all strategies")

        # ==============================
        # STEP 5: VALIDATE STRUCTURE
        # ==============================
        validated = validate_simulation_output(parsed)

        # ==============================
        # STEP 6: CONFIDENCE CALIBRATION
        # ==============================
        validated["confidence"] = calibrate_confidence(
            validated.get("confidence"), execution_mode
        )

        logger.info(
            f"[Trace:{trace_id}] MODE: {execution_mode} SUCCESS | "
            f"Action: {validated.get('predicted_action')} | "
            f"Confidence: {validated.get('confidence')}"
        )

        return build_response(validated, execution_mode), execution_mode

    except Exception as e:
        failure_mode = detect_ml_failure(e)

        logger.error(f"[Trace:{trace_id}] ERROR: {str(e)} -> Triggering {failure_mode}")

        if failure_mode == ExecutionMode.PARTIAL:
            resp = partial_response()
            resp["confidence"] = calibrate_confidence(resp["confidence"], ExecutionMode.PARTIAL)
            return build_response(resp, ExecutionMode.PARTIAL), ExecutionMode.PARTIAL

        return build_response(fallback_response(), ExecutionMode.FALLBACK), ExecutionMode.FALLBACK


# ==============================
# HELPERS
# ==============================
def _extract_memory_data(input_data: dict) -> dict:
    """
    Extracts memory retrieval data from the input_data payload.

    The simulation step receives the output of the memory_retrieval step
    as its input_data. This function normalizes the extraction.
    """
    if not isinstance(input_data, dict):
        return {"memory": [], "fallback": True}

    # 🔥 Check top-level first (direct output from memory_retrieval step)
    if "memory" in input_data:
        return input_data

    # Check nested formats (legacy or wrapped)
    raw = input_data.get("input_data") or input_data.get("data") or input_data

    if isinstance(raw, dict):
        # Wrapped data format
        data = raw.get("data", {})
        if isinstance(data, dict) and "memory" in data:
            return data
        
        # Or maybe it's just raw memory
        if "memory" in raw:
            return raw

    return {"memory": [], "fallback": True}