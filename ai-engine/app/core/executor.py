import time
import logging
from typing import Dict, Any

from app.schemas.request_schema import ExecuteRequest, ExecutionContext
from app.schemas.response_schema import ExecuteResponse
from app.core.registry import get_step_config
from app.core.execution_mode import ExecutionMode
from app.core.errors import (
    AIEngineException,
    ErrorType,
    SystemError,
    PermanentError,
    classify_error
)
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
        "user_id",
        "session_id",
        "domain",
        "game_id",
        "trace_id",
        "feature_version",
        "pipeline_version"
    ]

    for field in required_fields:
        if not getattr(context, field, None):
            raise PermanentError(f"Context integrity violation: Missing {field}")


def execute_pipeline_step(req: ExecuteRequest) -> ExecuteResponse:
    """
    Central execution entry point (Pure Orchestrator).

    Responsibilities:
    - Validate request + context
    - Load input (loader)
    - Execute processor ONCE (no retry logic)
    - Save output (saver)
    - Build response

    Rules:
    - Executor MUST NOT perform retries
    - Executor MUST NOT downgrade modes
    - Executor MUST NOT modify context
    - Processor handles FULL → PARTIAL → FALLBACK internally
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

        # 2. Deterministic Step Routing
        step_config = get_step_config(req.step)

        # 3. Loader: Fetch input data (domain-scoped)
        input_data = load_input_data(
            req.input_ref,
            req.context.model_dump()
        )

        # 4. Processor: SINGLE EXECUTION (NO RETRY LOGIC HERE)
        # Processor is responsible for handling execution modes internally
        result_data, execution_mode = step_config.processor_func(
            input_data=input_data,
            context=req.context.model_dump(),
            execution_mode=ExecutionMode.FULL
        )

        # 5. Saver: Persist output data (idempotent)
        output_ref = save_output_data(
            result_data,
            req.context.model_dump(),
            req.step,
            req.input_ref
        )

        execution_time_ms = int((time.time() - start_time) * 1000)

        # 6. Logging (observability)
        logger.info(
            f"[Trace: {trace_id}] "
            f"Step: {req.step} | Mode: {execution_mode} | Output: {output_ref}"
        )

        # 7. Response Builder
        return build_success_response(
            output_ref=output_ref,
            next_step=step_config.next_step,
            execution_mode=execution_mode,
            resolved_model_version=req.context.resolved_model_version,
            execution_time_ms=execution_time_ms
        )

    except Exception as e:
        # Deterministic Error Classification (NO raw exceptions leak)
        classified_error = classify_error(e)
        execution_time_ms = int((time.time() - start_time) * 1000)

        logger.error(
            f"[Trace: {trace_id}] "
            f"{classified_error.error_type}: {classified_error.message}"
        )

        return build_error_response(
            error_type=classified_error.error_type,
            message=classified_error.message,
            execution_mode=ExecutionMode.FALLBACK,
            execution_time_ms=execution_time_ms,
            details=getattr(classified_error, "details", {}),
            next_step=None  # ensure contract consistency
        )