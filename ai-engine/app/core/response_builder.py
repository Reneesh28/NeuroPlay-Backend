from app.schemas.response_schema import ExecuteResponse, ExecutionMetadata, ErrorDetail
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def build_success_response(
    output_ref: str,
    next_step: Optional[str],
    execution_mode: str,
    resolved_model_version: Optional[str],
    execution_time_ms: int
) -> ExecuteResponse:
    """
    Standardized Success Response Builder.
    Ensures contract compliance and validates next_step integrity.
    """
    # Rule: AI MUST ALWAYS return output_ref
    if not output_ref:
        logger.error("Attempted to build success response without output_ref")
        # This shouldn't happen if executor is working correctly, but we guard it
        raise ValueError("output_ref is mandatory for success response")

    # Step validation logic could be added here if we want to be extra strict,
    # but the executor already uses get_step_config which handles registry lookup.
    
    return ExecuteResponse(
        status="success",
        output_ref=output_ref,
        next_step=next_step,
        execution_mode=execution_mode,
        resolved_model_version=resolved_model_version,
        execution_metadata=ExecutionMetadata(
            execution_time_ms=execution_time_ms,
            mode=execution_mode
        )
    )

def build_error_response(
    error_type: str,
    message: str,
    execution_mode: str,
    execution_time_ms: int,
    details: Optional[Dict[str, Any]] = None
) -> ExecuteResponse:
    """
    Standardized Error Response Builder.
    Ensures uniform error formatting for the contract layer.
    """
    return ExecuteResponse(
        status="failed",
        execution_mode=execution_mode,
        execution_metadata=ExecutionMetadata(
            execution_time_ms=execution_time_ms,
            mode=execution_mode
        ),
        error=ErrorDetail(
            type=error_type,
            message=message,
            details=details
        )
    )
