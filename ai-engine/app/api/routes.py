from fastapi import APIRouter
from app.schemas.request_schema import ExecuteRequest
from app.core.router import execute_step

router = APIRouter()

@router.post("/ai/execute")
async def execute(req: ExecuteRequest):
    return execute_step(req)