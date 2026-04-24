import time
import logging
from typing import Dict, Any

from app.schemas.request_schema import ExecuteRequest, ExecutionContext
from app.schemas.response_schema import ExecuteResponse
from app.core.registry import get_step_config
from app.core.execution_mode import run_with_fallback, ExecutionMode
from app.core.errors import AIEngineException, ErrorType, SystemError, PermanentError, classify_error
from app.core.response_builder import build_success_response, build_error_response
from app.pipeline.loader import load_input_data
from app.pipeline.saver import save_output_data

logger = logging.getLogger(__name__)

def _validate_context(context: ExecutionContext):
    """
    Mandatory validation of execution context integrity.
    Reject execution if any field is missing or inconsistent.
    """
    required_fields = [
        "domain", "game_id", "trace_id", 
        "feature_version", "pipeline_version"
    ]
    for field in required_fields:
        if not getattr(context, field, None):
            raise PermanentError(f"Context integrity violation: Missing {field}")

def execute_pipeline_step(req: ExecuteRequest) -> ExecuteResponse:
    """
    Central execution entry point (Pure Orchestrator).
    Orchestrates: loader -> processor -> saver.
    Enforces idempotency and context immutability.
    """
    start_time = time.time()
    trace_id = req.context.trace_id
    
    try:
        # 1. Context & Request Validation
        _validate_context(req.context)
        if not req.input_ref:
            raise PermanentError("input_ref is required")
        if not req.step:
            raise PermanentError("step is required")

        # 2. Fetch step configuration (Deterministic Router)
        step_config = get_step_config(req.step)
        
        # 3. Loader: Fetch input data (Domain-Scoped)
        # Executor does NOT access DB directly
        input_data = load_input_data(req.input_ref, req.context.model_dump())
        
        # 4. Processor: Execute with monotonic downgrade logic
        # Rule: same (input_ref + context + step) -> same output_ref
        result_data, mode = run_with_fallback(
            processor_func=step_config.processor_func,
            input_data=input_data,
            context=req.context.model_dump()
        )
        
        # 5. Saver: Persist output data
        # Executor does NOT access DB directly
        output_ref = save_output_data(result_data, req.context.model_dump())
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # 6. Response Builder: Standardized response construction
        logger.info(f"[Trace: {trace_id}] Step: {req.step} | Mode: {mode} | Output: {output_ref}")
        
        return build_success_response(
            output_ref=output_ref,
            next_step=step_config.next_step,
            execution_mode=mode,
            resolved_model_version=req.context.resolved_model_version,
            execution_time_ms=execution_time_ms
        )
        
    except Exception as e:
        # Deterministic Classification: Ensure NO raw exceptions leak
        classified_error = classify_error(e)
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        logger.error(f"[Trace: {trace_id}] {classified_error.error_type}: {classified_error.message}")
        
        return build_error_response(
            error_type=classified_error.error_type,
            message=classified_error.message,
            execution_mode=ExecutionMode.FALLBACK,
            execution_time_ms=execution_time_ms,
            details=getattr(classified_error, 'details', {})
        )
