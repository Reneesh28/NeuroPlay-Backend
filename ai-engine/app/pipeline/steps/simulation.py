import logging
import json

from app.core.execution_mode import ExecutionMode, detect_ml_failure
from app.models.llm_loader import call_llm
from app.prompting.templates import build_simulation_prompt
from app.utils.output_parser import parse_llm_output
from app.pipeline.validators.simulation_output import validate_simulation_output
from app.core.response_builder import build_response

logger = logging.getLogger(__name__)


def calibrate_confidence(confidence, mode):
    try:
        confidence = float(confidence)
    except:
        confidence = 0.5

    if mode == ExecutionMode.FULL:
        return min(confidence, 0.85)

    elif mode == ExecutionMode.PARTIAL:
        return min(confidence, 0.6)

    return 0.5


def fallback_response():
    return {
        "predicted_action": "hold position",
        "confidence": 0.5,
        "reasoning": "Fallback action applied due to system uncertainty",
        "coaching_tip": "Play safe and gather information"
    }


def partial_response():
    return {
        "predicted_action": "hold position",
        "confidence": 0.6,
        "reasoning": "System degraded, applying conservative strategy",
        "coaching_tip": "Focus on safety and positioning"
    }


def run(input_data: dict, context: dict, execution_mode: str) -> tuple:
    trace_id = context.get("trace_id", "unknown")

    # 🔥 HARD GUARD: invalid input
    if not input_data or not isinstance(input_data, dict):
        logger.warning(f"[Trace:{trace_id}] Invalid input_data → fallback")
        return build_response(fallback_response(), ExecutionMode.FALLBACK), ExecutionMode.FALLBACK

    if execution_mode == ExecutionMode.FALLBACK:
        logger.info(f"[Trace:{trace_id}] MODE: FALLBACK (pre-triggered)")
        return build_response(fallback_response(), ExecutionMode.FALLBACK), ExecutionMode.FALLBACK

    try:
        # ==============================
        # PROMPT
        # ==============================
        prompt = build_simulation_prompt(input_data, context, execution_mode)

        logger.info(f"[Trace:{trace_id}] PROMPT GENERATED")

        # ==============================
        # LLM CALL
        # ==============================
        raw = call_llm(prompt)

        if not raw:
            raise Exception("LLM returned empty response")

        # ==============================
        # SAFE PARSE (DOUBLE LAYER)
        # ==============================
        try:
            parsed = parse_llm_output(raw)
        except Exception:
            logger.warning(f"[Trace:{trace_id}] Primary parse failed → retry json.loads")

            try:
                parsed = json.loads(raw)
            except:
                raise Exception("Failed to parse LLM output")

        if not parsed:
            raise Exception("Parsed output empty")

        # ==============================
        # VALIDATE STRUCTURE
        # ==============================
        validated = validate_simulation_output(parsed)

        # ==============================
        # CONFIDENCE CONTROL
        # ==============================
        validated["confidence"] = calibrate_confidence(
            validated.get("confidence"), execution_mode
        )

        logger.info(f"[Trace:{trace_id}] MODE: {execution_mode} SUCCESS")

        return build_response(validated, execution_mode), execution_mode

    except Exception as e:
        failure_mode = detect_ml_failure(e)

        logger.error(f"[Trace:{trace_id}] ERROR: {str(e)} -> Triggering {failure_mode}")

        if failure_mode == ExecutionMode.PARTIAL:
            return build_response(partial_response(), ExecutionMode.PARTIAL), ExecutionMode.PARTIAL

        return build_response(fallback_response(), ExecutionMode.FALLBACK), ExecutionMode.FALLBACK