import logging

from app.core.execution_mode import ExecutionMode
from app.models.llm_loader import call_llm
from app.prompting.templates import build_simulation_prompt
from app.utils.output_parser import parse_llm_output
from app.pipeline.validators.simulation_output import validate_simulation_output
from app.core.response_builder import normalize_simulation_output
from app.core.error_classifier import classify_exception

logger = logging.getLogger(__name__)




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

        return normalize_simulation_output(output), ExecutionMode.FALLBACK

    try:
        logger.info(f"[Trace: {trace_id}] Simulation {current_mode}")

        # 🔹 Build prompt
        prompt = build_simulation_prompt(
            input_data=input_data,
            context=context,
            mode=current_mode
        )
        logger.debug(f"[Trace: {trace_id}] Mode: {current_mode} | Prompt: {prompt}")

        # 🔹 Call LLM
        raw_response = call_llm(prompt)
        logger.info(f"[Trace: {trace_id}] LLM call completed")
        logger.debug(f"[Trace: {trace_id}] Raw Response: {raw_response}")

        if raw_response is None:
            raise Exception("LLM returned None")

        # 🔹 Parse output
        parsed = parse_llm_output(raw_response)
        logger.info(f"[Trace: {trace_id}] Parsing successful")
        logger.debug(f"[Trace: {trace_id}] Parsed Data: {parsed}")

        # 🔹 Validate schema
        validated = validate_simulation_output(parsed)

        # 🔹 Confidence calibration (Strict System Control)
        raw_confidence = validated.get("confidence", 0.5)

        if current_mode == ExecutionMode.FULL:
            # Optimal mode: Cap at 0.9 to maintain healthy skepticism
            validated["confidence"] = min(raw_confidence, 0.9)

        elif current_mode == ExecutionMode.PARTIAL:
            # Degraded mode: Cap at 0.65 to signal caution
            validated["confidence"] = min(raw_confidence, 0.65)

        else:
            # Fallback/System failure: Fixed at 0.5 (Neutral)
            validated["confidence"] = 0.5

        # 🔹 Normalize output
        final_output = normalize_simulation_output(validated)

        # 🔹 Log output (important for debugging)
        logger.info(f"[Trace: {trace_id}] Output: {final_output}")

        return final_output, current_mode

    except Exception as e:
        category = classify_exception(e)
        logger.error(f"[Trace: {trace_id}] LLM failure [{category}]: {str(e)}")

        if current_mode == ExecutionMode.FULL:
            logger.warning(f"[Trace: {trace_id}] Downgrading FULL → PARTIAL")

            output = {
                "predicted_action": "hold position",
                "confidence": 0.6,
                "reasoning": "Partial mode due to degraded AI",
                "coaching_tip": "Focus on positioning"
            }

            return normalize_simulation_output(output), ExecutionMode.PARTIAL

        logger.warning(f"[Trace: {trace_id}] Falling back to safe mode")

        try:
            output = {
                "predicted_action": "hold position",
                "confidence": 0.5,
                "reasoning": "Fallback after system failure",
                "coaching_tip": "Play safe"
            }
            return normalize_simulation_output(output), ExecutionMode.FALLBACK
        except Exception:
            # 🚨 EMERGENCY FALLBACK (No logic, just raw dict)
            return {
                "predicted_action": "hold position",
                "confidence": 0.5,
                "reasoning": "Critical engine failure",
                "coaching_tip": "Restarting engine recommended"
            }, ExecutionMode.FALLBACK