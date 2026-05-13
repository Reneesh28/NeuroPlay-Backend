import logging
import sys
import os

# Ensure 'features' module is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.core.errors import MLError, PartialExecutionTrigger
from app.core.execution_mode import ExecutionMode
from features.feature_extraction import run_feature_extraction

logger = logging.getLogger(__name__)

# 🔥 CRITICAL: fixed vector dimension
VECTOR_DIM = 20


def _fix_vector(vector):
    """
    Ensures vector is always valid 20D numeric list
    (NO FAILURES — auto-correct instead)
    """
    if not isinstance(vector, list):
        logger.warning("ml_input not list → converting to default vector")
        return [0.0] * VECTOR_DIM

    # Convert values to float safely
    safe_vector = []
    for v in vector:
        try:
            safe_vector.append(float(v))
        except Exception:
            safe_vector.append(0.0)

    # Fix dimension
    if len(safe_vector) < VECTOR_DIM:
        safe_vector += [0.0] * (VECTOR_DIM - len(safe_vector))
    elif len(safe_vector) > VECTOR_DIM:
        safe_vector = safe_vector[:VECTOR_DIM]

    return safe_vector


def run(input_data: dict, context: dict, execution_mode: str) -> tuple:
    trace_id = context.get("trace_id", "unknown")
    current_mode = execution_mode

    # ======================
    # FULL MODE
    # ======================
    if current_mode == ExecutionMode.FULL:
        try:
            logger.info(f"[Trace: {trace_id}] Feature Extraction START (Mode: FULL)")

            result = run_feature_extraction(input_data)

            if not isinstance(result, dict):
                raise MLError("Feature extraction result is not a dictionary")

            raw_features = result.get("features", {})
            norm_features = result.get("normalized_features", {})
            vector = result.get("ml_input")
            status = result.get("feature_status", {})
            missing = result.get("missing_features", [])

            # --- STRUCTURED DEBUG LOGGING (STEP 8) ---
            logger.info(f"[Trace: {trace_id}] DIAGNOSTICS:")
            logger.info(f"  - MISSING SOURCES: {missing}")
            logger.info(f"  - FEATURE STATUS: {status}")
            logger.info(f"  - ML VECTOR (HEAD 5): {vector[:5] if vector else 'None'}")

            # --- CRITICAL FEATURE VALIDATION (STEP 7) ---
            critical_features = ["movement_speed", "accuracy", "damage_dealt"]
            failed_critical = [f for f in critical_features if status.get(f) == "missing_source"]
            
            if failed_critical:
                logger.warning(f"[Trace: {trace_id}] Missing critical telemetry: {failed_critical}")
                raise PartialExecutionTrigger(f"Missing critical telemetry: {failed_critical}")

            if vector is None:
                raise MLError("ml_input missing from feature extraction")

            # 🔥 SAFE FIX (NO HARD FAIL)
            vector = _fix_vector(vector)

            output = {
                "features": raw_features,
                "normalized_features": norm_features,
                "ml_input": vector,
                "diagnostics": {
                    "status": status,
                    "missing": missing
                }
            }

            return output, ExecutionMode.FULL

        except (MLError, PartialExecutionTrigger) as e:
            logger.warning(f"[Trace: {trace_id}] Degrading to PARTIAL: {str(e)}")
            current_mode = ExecutionMode.PARTIAL

        except Exception as e:
            logger.error(f"[Trace: {trace_id}] Unexpected error in FULL: {str(e)}")
            current_mode = ExecutionMode.PARTIAL


    # ======================
    # PARTIAL MODE
    # ======================
    if current_mode == ExecutionMode.PARTIAL:
        try:
            logger.info(f"[Trace: {trace_id}] Feature PARTIAL")

            raw = {
                "movement_speed": 0.5,
                "aim_stability": 0.5
            }

            vector = [0.5] * VECTOR_DIM

            output = {
                "features": raw,
                "normalized_features": raw,
                "ml_input": vector,
                "partial": True
            }

            print("PROCESSOR PARTIAL OUTPUT:", output)  # 🔥 DEBUG

            return output, ExecutionMode.PARTIAL

        except Exception as e:
            logger.error(f"[Trace: {trace_id}] Error in PARTIAL mode: {str(e)}")
            current_mode = ExecutionMode.FALLBACK

    # ======================
    # FALLBACK MODE
    # ======================
    logger.warning(f"[Trace: {trace_id}] Feature FALLBACK")

    output = {
        "features": {},
        "normalized_features": {},
        "ml_input": [0.0] * VECTOR_DIM,
        "fallback": True,
        "confidence": 0.0
    }

    print("PROCESSOR FALLBACK OUTPUT:", output)  # 🔥 DEBUG

    return output, ExecutionMode.FALLBACK