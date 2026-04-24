from typing import Callable, Optional, Dict, Any
from app.processors.video_processor import process_video
from app.processors.feature_processor import process_feature 
from app.processors.embedding_processor import process_embedding
from app.processors.clustering_processor import process_clustering
from app.processors.simulation_processor import process_simulation
from app.core.errors import PermanentError

class StepConfig:
    def __init__(self, processor_func: Callable, next_step: Optional[str]):
        self.processor_func = processor_func
        self.next_step = next_step

STEP_REGISTRY: Dict[str, StepConfig] = {
    "video_processing": StepConfig(process_video, "feature_extraction"),
    "feature_extraction": StepConfig(process_feature, "embedding_generation"),
    "embedding_generation": StepConfig(process_embedding, "clustering"),
    "clustering": StepConfig(process_clustering, "simulation"),
    "simulation": StepConfig(process_simulation, None)
}

def get_step_config(step_name: str) -> StepConfig:
    """Returns the processor and next step configuration for a given step."""
    if step_name not in STEP_REGISTRY:
        raise PermanentError(
            message=f"Unknown or unregistered step: {step_name}",
            details={"step": step_name, "valid_steps": list(STEP_REGISTRY.keys())}
        )
    return STEP_REGISTRY[step_name]
