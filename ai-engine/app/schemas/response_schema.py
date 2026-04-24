from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ExecutionMetadata(BaseModel):
    execution_time_ms: int
    mode: str = Field(..., description="FULL, PARTIAL, or FALLBACK")

class ErrorDetail(BaseModel):
    type: str = Field(..., description="TRANSIENT, SYSTEM, or PERMANENT")
    message: str
    details: Optional[Dict[str, Any]] = None

class ExecuteResponse(BaseModel):
    status: str = Field(..., description="success or failed")
    output_ref: Optional[str] = None
    next_step: Optional[str] = None
    resolved_model_version: Optional[str] = None
    execution_metadata: ExecutionMetadata
    error: Optional[ErrorDetail] = None
