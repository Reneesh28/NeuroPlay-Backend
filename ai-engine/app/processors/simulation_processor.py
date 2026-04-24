import logging
from app.core.execution_mode import ExecutionMode
from app.core.errors import MLError, PartialExecutionTrigger

logger = logging.getLogger(__name__)


def run(input_data: dict, context: dict, execution_mode: str) -> tuple:
    trace_id = context.get("trace_id", "unknown")

    current_mode = execution_mode

    if current_mode == ExecutionMode.FULL:
        try:
            logger.info(f"[Trace: {trace_id}] Simulation FULL")
            return {"result": "high_fidelity_simulation_complete"}, ExecutionMode.FULL

        except (MLError, PartialExecutionTrigger):
            current_mode = ExecutionMode.PARTIAL

    if current_mode == ExecutionMode.PARTIAL:
        try:
            logger.info(f"[Trace: {trace_id}] Simulation PARTIAL")
            return {"result": "low_fidelity_simulation_complete", "partial": True}, ExecutionMode.PARTIAL

        except Exception:
            current_mode = ExecutionMode.FALLBACK

    logger.info(f"[Trace: {trace_id}] Simulation FALLBACK")

    return {
        "result": "heuristic_simulation_complete",
        "fallback": True,
        "confidence": 0.0
    }, ExecutionMode.FALLBACK