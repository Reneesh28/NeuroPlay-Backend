from typing import Callable, Optional, Dict, Any
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

STEP_REGISTRY: Dict[str, StepConfig] = {
    "video_processing": StepConfig(video_processor.run, "feature_extraction"),
    "feature_extraction": StepConfig(feature_processor.run, "embedding_generation"),
    "embedding_generation": StepConfig(embedding_processor.run, "clustering"),
    "clustering": StepConfig(clustering_processor.run, "simulation"),
    "simulation": StepConfig(simulation_processor.run, None)
}

def get_step_config(step_name: str) -> StepConfig:
    """Returns the processor and next step configuration for a given step."""
    if step_name not in STEP_REGISTRY:
        raise PermanentError(
            message=f"Unknown or unregistered step: {step_name}",
            details={"step": step_name, "valid_steps": list(STEP_REGISTRY.keys())}
        )
    return STEP_REGISTRY[step_name]
