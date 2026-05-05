from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.errors import classify_error
import logging

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    classified_error = classify_error(exc)
    
    logger.error(f"Global Error Catch: {classified_error.error_type} - {classified_error.message}")
    
    return JSONResponse(
        status_code=500 if classified_error.error_type != "PERMANENT" else 400,
        content={
            "status": "failed",
            "error_type": classified_error.error_type,
            "message": classified_error.message
        }
    )