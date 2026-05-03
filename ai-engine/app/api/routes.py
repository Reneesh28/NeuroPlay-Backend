from fastapi import APIRouter
from app.schemas.request_schema import ExecuteRequest
from app.schemas.response_schema import ExecuteResponse
from app.core.executor import execute_pipeline_step

from app.api.search import router as search_router

router = APIRouter()

# ==============================
# CORE EXECUTION ROUTE
# ==============================
@router.post("/execute", response_model=ExecuteResponse)
async def execute(req: ExecuteRequest) -> ExecuteResponse:
    return execute_pipeline_step(req)


# ==============================
# STEP-SPECIFIC ROUTES
# ==============================
def execute_step_wrapper(step_name: str, req: ExecuteRequest):
    req.step = step_name
    return execute_pipeline_step(req)


@router.post("/embedding-generation", response_model=ExecuteResponse)
async def embedding_generation(req: ExecuteRequest):
    return execute_step_wrapper("embedding_generation", req)


@router.post("/memory-retrieval", response_model=ExecuteResponse)
async def memory_retrieval(req: ExecuteRequest):
    return execute_step_wrapper("memory_retrieval", req)


# ==============================
# SEARCH ROUTES
# ==============================
router.include_router(search_router, prefix="/api")