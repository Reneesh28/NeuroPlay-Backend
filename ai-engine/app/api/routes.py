from fastapi import APIRouter
from app.schemas.request_schema import ExecuteRequest
from app.schemas.response_schema import ExecuteResponse
from app.core.executor import execute_pipeline_step

router = APIRouter()

@router.post("/ai/execute", response_model=ExecuteResponse)
async def execute(req: ExecuteRequest) -> ExecuteResponse:
    return execute_pipeline_step(req)