from pydantic import BaseModel
from typing import Dict, Any

class ExecuteRequest(BaseModel):
    job_id: str
    step: str
    input: Dict[str, Any]