from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Union

class ExecutionContext(BaseModel):
    user_id: str
    session_id: Union[str, None] = None # 🔥 Allow explicit nulls
    domain: str = Field(..., description="Mandatory domain field for isolated execution")
    game_id: str
    requested_model_version: Union[str, None] = None
    resolved_model_version: Union[str, None] = None
    feature_version: Union[str, None] = None
    pipeline_version: Union[str, None] = None
    trace_id: str

class ExecuteRequest(BaseModel):
    job_id: str
    step: str
    input_ref: Any # 🔥 Nuclear option: allow anything for now to bypass 422
    input_type: str
    context: ExecutionContext
