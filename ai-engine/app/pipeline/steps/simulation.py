import logging

from app.core.execution_mode import ExecutionMode
from app.models.llm_loader import call_llm
from app.prompting.templates import build_simulation_prompt
from app.utils.output_parser import parse_llm_output
from app.pipeline.validators.simulation_output import validate_simulation_output

logger = logging.getLogger(__name__)


def _normalize_output(data: dict) -> dict:
    """
    Ensures consistent structure and safe values
    """

    return {
        "predicted_action": str(data.get("predicted_action", "hold position")),
        "confidence": float(max(0.0, min(data.get("confidence", 0.5), 1.0))),
        "reasoning": str(data.get("reasoning", ""))[:300],  # limit length
        "coaching_tip": str(data.get("coaching_tip", ""))[:200]
    }


def run(input_data: dict, context: dict, execution_mode: str) -> tuple:
    """
    Simulation step with LLM + prompt + parser + validation + consistency layer
    """

    trace_id = context.get("trace_id", "unknown")
    current_mode = execution_mode

    # 🔹 FALLBACK MODE (NO LLM)
    if current_mode == ExecutionMode.FALLBACK:
        logger.info(f"[Trace: {trace_id}] Simulation FALLBACK")

        output = {
            "predicted_action": "hold position",
            "confidence": 0.5,
            "reasoning": "Fallback logic applied",
            "coaching_tip": "Play safe and gather more information"
        }

        return _normalize_output(output), ExecutionMode.FALLBACK

    try:
        logger.info(f"[Trace: {trace_id}] Simulation {current_mode}")

        # 🔹 Build prompt
        prompt = build_simulation_prompt(
            input_data=input_data,
            context=context,
            mode=current_mode
        )

        # 🔹 Call LLM
        raw_response = call_llm(prompt)

        if raw_response is None:
            raise Exception("LLM returned None")

        # 🔹 Parse output
        parsed = parse_llm_output(raw_response)

        # 🔹 Validate schema
        validated = validate_simulation_output(parsed)

        # 🔹 Confidence calibration
        confidence = validated.get("confidence", 0.5)

        if current_mode == ExecutionMode.FULL:
            validated["confidence"] = min(confidence, 0.95)

        elif current_mode == ExecutionMode.PARTIAL:
            validated["confidence"] = min(confidence, 0.7)

        else:
            validated["confidence"] = 0.5

        # 🔹 Normalize output
        final_output = _normalize_output(validated)

        # 🔹 Log output (important for debugging)
        logger.info(f"[Trace: {trace_id}] Output: {final_output}")

        return final_output, current_mode

    except Exception as e:
        logger.error(f"[Trace: {trace_id}] LLM failure: {str(e)}")

        if current_mode == ExecutionMode.FULL:
            logger.warning(f"[Trace: {trace_id}] Downgrading FULL → PARTIAL")

            output = {
                "predicted_action": "hold position",
                "confidence": 0.6,
                "reasoning": "Partial mode due to degraded AI",
                "coaching_tip": "Focus on positioning"
            }

            return _normalize_output(output), ExecutionMode.PARTIAL

        logger.warning(f"[Trace: {trace_id}] Falling back to safe mode")

        output = {
            "predicted_action": "hold position",
            "confidence": 0.5,
            "reasoning": "Fallback after system failure",
            "coaching_tip": "Play safe"
        }

        return _normalize_output(output), ExecutionMode.FALLBACK