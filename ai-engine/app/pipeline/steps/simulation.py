import logging
from app.core.execution_mode import ExecutionMode
from app.models.llm_loader import call_llm
from app.prompting.templates import build_simulation_prompt
from app.utils.output_parser import parse_llm_output
from app.pipeline.validators.simulation_output import validate_simulation_output
from app.core.response_builder import build_response
from app.core.error_classifier import classify_error

logger = logging.getLogger(__name__)


def calibrate_confidence(confidence, mode):
    try:
        confidence = float(confidence)
    except:
        confidence = 0.5

    if mode == ExecutionMode.FULL:
        return min(confidence, 0.9)

    elif mode == ExecutionMode.PARTIAL:
        return min(confidence, 0.6)

    return 0.5


def fallback_response():
    return {
        "predicted_action": "hold position",
        "confidence": 0.5,
        "reasoning": "Fallback action applied",
        "coaching_tip": "Play safe and gather info"
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

    if execution_mode == ExecutionMode.FALLBACK:
        logger.info(f"[Trace: {trace_id}] MODE: {execution_mode}")
        return build_response(fallback_response(), execution_mode), ExecutionMode.FALLBACK

    try:
        # 🔹 Prompt
        prompt = build_simulation_prompt(input_data, context, execution_mode)
        logger.info(f"[Trace: {trace_id}] PROMPT: {prompt}")

        # 🔹 LLM Call
        raw = call_llm(prompt)
        logger.info(f"[Trace: {trace_id}] RAW RESPONSE: {raw}")

        if not raw:
            raise Exception("LLM returned empty response")

        # 🔹 Parse
        parsed = parse_llm_output(raw)
        logger.info(f"[Trace: {trace_id}] PARSED: {parsed}")

        if not parsed:
            raise Exception("Parsed output is empty")

        # 🔹 Validate
        validated = validate_simulation_output(parsed)

        # 🔹 Confidence control
        validated["confidence"] = calibrate_confidence(
            validated.get("confidence"), execution_mode
        )

        logger.info(f"[Trace: {trace_id}] MODE: {execution_mode}")

        return build_response(validated, execution_mode), execution_mode

    except Exception as e:
        error_type = classify_error(e)
        logger.error(f"[Trace: {trace_id}] {error_type}: {str(e)}")

        if error_type == "TRANSIENT":
            return build_response(partial_response(), ExecutionMode.PARTIAL), ExecutionMode.PARTIAL

        return build_response(fallback_response(), ExecutionMode.FALLBACK), ExecutionMode.FALLBACK