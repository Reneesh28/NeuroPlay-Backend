from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ExecutionContext(BaseModel):
    user_id: str
    session_id: str
    domain: str = Field(..., description="Mandatory domain field for isolated execution")
    game_id: str
    requested_model_version: Optional[str] = None
    resolved_model_version: Optional[str] = None
    feature_version: Optional[str] = None
    pipeline_version: Optional[str] = None
    trace_id: str

class ExecuteRequest(BaseModel):
    job_id: str
    step: str
    input_ref: Optional[str] = None
    context: ExecutionContext
