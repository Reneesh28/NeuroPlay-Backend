import time
import logging
from app.schemas.request_schema import ExecuteRequest
from app.schemas.response_schema import ExecuteResponse, ExecutionMetadata, ErrorDetail
from app.core.registry import get_step_config
from app.core.execution_mode import run_with_fallback, ExecutionMode
from app.core.errors import AIEngineException, ErrorType, SystemError

logger = logging.getLogger(__name__)

def execute_pipeline_step(req: ExecuteRequest) -> ExecuteResponse:
    """
    Central execution entry point.
    Validates context, routes to the correct processor, applies fallback logic,
    and formats the response according to the strict contract.
    """
    start_time = time.time()
    
    try:
        if not req.input_ref:
            raise SystemError("input_ref is required")

        if not req.step:
            raise SystemError("step is required")

        # 1. Fetch step configuration (registry validation)
        step_config = get_step_config(req.step)
        
        # 2. Execute with graceful fallback
        result, mode = run_with_fallback(
            processor_func=step_config.processor_func,
            input_ref=req.input_ref,
            context=req.context.model_dump()
        )
        
        # Calculate execution time
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        result["execution_mode"] = mode

        # Ensure valid output
        if not isinstance(result, dict):
            raise SystemError("Processor must return a dictionary")
            
        required_keys = ["output_ref"]
        for key in required_keys:
            if key not in result:
                raise SystemError(f"Missing required key: {key}")
            
        output_ref = result["output_ref"]
        
        # 3. Build Response
        trace_id = req.context.trace_id if hasattr(req.context, "trace_id") else "unknown"
        logger.info(f"[Trace: {trace_id}] Step: {req.step} | Mode: {mode} | Next: {step_config.next_step}")
        
        return ExecuteResponse(
            status="success",
            output_ref=output_ref,
            next_step=step_config.next_step,
            resolved_model_version=req.context.resolved_model_version,
            execution_metadata=ExecutionMetadata(
                execution_time_ms=execution_time_ms,
                mode=mode
            )
        )
        
    except AIEngineException as e:
        # Caught a classified error (Transient, System, Permanent)
        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Execution failed for step {req.step}: {e.message}")
        
        return ExecuteResponse(
            status="failed",
            execution_metadata=ExecutionMetadata(
                execution_time_ms=execution_time_ms,
                mode=ExecutionMode.FALLBACK
            ),
            error=ErrorDetail(
                type=e.error_type,
                message=e.message,
                details=e.details
            )
        )
        
    except Exception as e:
        # Unhandled critical error that wasn't caught by the fallback engine
        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Unhandled critical crash in executor: {str(e)}")
        
        return ExecuteResponse(
            status="failed",
            execution_metadata=ExecutionMetadata(
                execution_time_ms=execution_time_ms,
                mode=ExecutionMode.FALLBACK
            ),
            error=ErrorDetail(
                type=ErrorType.SYSTEM,
                message=f"Critical unhandled execution failure: {str(e)}"
            )
        )
