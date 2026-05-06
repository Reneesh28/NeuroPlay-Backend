"""
Simulation Processor — Phase 7: Digital Twin Reasoning Layer

This processor is registered in the step registry and delegates
execution to the Phase 7 simulation step (pipeline/steps/simulation.py).

It handles the execution mode cascade:
  FULL → PARTIAL → FALLBACK

The actual intelligence (context building, LLM call, parsing)
lives in app.pipeline.steps.simulation.run().
"""

import logging
from app.core.execution_mode import ExecutionMode
from app.pipeline.steps.simulation import run as simulation_run

logger = logging.getLogger(__name__)


def run(input_data: dict, context: dict, execution_mode: str) -> tuple:
    """
    Entry point for the simulation processor.

    Delegates directly to the Phase 7 simulation step which handles:
    - Context building
    - Prompt generation
    - LLM execution with retries
    - Output parsing and validation
    - Confidence calibration
    - Mode-based fallback cascade

    Args:
        input_data:      Raw pipeline input
        context:         Execution context dict
        execution_mode:  Current execution mode (FULL / PARTIAL / FALLBACK)

    Returns:
        Tuple of (result_dict, execution_mode_str)
    """
    trace_id = context.get("trace_id", "unknown")

    logger.info(
        f"[Trace:{trace_id}] Simulation processor invoked | "
        f"Mode: {execution_mode}"
    )

    return simulation_run(
        input_data=input_data,
        context=context,
        execution_mode=execution_mode
    )