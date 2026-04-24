from typing import Callable, Optional, Dict
from app.processors import (
    video_processor,
    feature_processor,
    embedding_processor,
    clustering_processor,
    simulation_processor
)
from app.core.errors import PermanentError


class StepConfig:
    def __init__(self, processor_func: Callable, next_step: Optional[str]):
        self.processor_func = processor_func
        self.next_step = next_step


# 🔥 CENTRAL STEP REGISTRY (DETERMINISTIC ROUTING)
STEP_REGISTRY: Dict[str, StepConfig] = {
    "video_processing": StepConfig(
        processor_func=video_processor.run,
        next_step="feature_extraction"
    ),
    "feature_extraction": StepConfig(
        processor_func=feature_processor.run,
        next_step="embedding_generation"
    ),
    "embedding_generation": StepConfig(
        processor_func=embedding_processor.run,
        next_step="clustering"
    ),
    "clustering": StepConfig(
        processor_func=clustering_processor.run,
        next_step="simulation"
    ),
    "simulation": StepConfig(
        processor_func=simulation_processor.run,
        next_step=None  # 🔥 Final step
    )
}


def get_step_config(step_name: str) -> StepConfig:
    """
    Returns the processor and next step configuration for a given step.
    Enforces strict contract: unknown step = hard fail.
    """
    config = STEP_REGISTRY.get(step_name)

    if not config:
        raise PermanentError(
            message=f"Unknown or unregistered step: {step_name}",
            details={
                "step": step_name,
                "valid_steps": list(STEP_REGISTRY.keys())
            }
        )

    return config