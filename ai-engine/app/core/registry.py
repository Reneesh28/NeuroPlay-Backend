from typing import Callable, Optional, Dict
from app.processors import (
    video_processor,
    feature_processor,
    embedding_processor,
    simulation_processor
)
from app.pipeline.steps.memory_retrieval import run as memory_retrieval_run
from app.core.errors import PermanentError


class StepConfig:
    def __init__(self, processor_func: Callable, next_step: Optional[str]):
        self.processor_func = processor_func
        self.next_step = next_step


# 🔥 CENTRAL STEP REGISTRY (UPDATED)
STEP_REGISTRY: Dict[str, StepConfig] = {
    "video_processing": StepConfig(
        processor_func=video_processor.run,
        next_step="feature_extraction"
    ),

    "feature_extraction": StepConfig(
        processor_func=feature_processor.run,
        next_step="embedding_generation"
    ),

    # 🔥 STEP 1: embedding
    "embedding_generation": StepConfig(
        processor_func=embedding_processor.run,
        next_step="memory_retrieval"
    ),

    # 🔥 STEP 2: memory
    "memory_retrieval": StepConfig(
        processor_func=memory_retrieval_run,
        next_step="simulation"
    ),

    # 🔥 FINAL STEP
    "simulation": StepConfig(
        processor_func=simulation_processor.run,
        next_step=None
    )
}


def get_step_config(step_name: str) -> StepConfig:
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