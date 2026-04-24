from enum import Enum
from typing import Dict, Any, Optional, Type
import logging

logger = logging.getLogger(__name__)

class ErrorType(str, Enum):
    TRANSIENT = "TRANSIENT"
    SYSTEM = "SYSTEM"
    PERMANENT = "PERMANENT"
    ML_FAILURE = "ML_FAILURE"

class AIEngineException(Exception):
    """Base exception for all AI Engine errors."""
    def __init__(self, message: str, error_type: ErrorType, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details or {}

class TransientError(AIEngineException):
    """Errors that can be retried (e.g., timeouts)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.TRANSIENT, details)

class SystemError(AIEngineException):
    """Internal system errors (e.g., unexpected crashes)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.SYSTEM, details)

class PermanentError(AIEngineException):
    """Errors that should NOT be retried (e.g., invalid step)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.PERMANENT, details)

class MLError(AIEngineException):
    """Errors specifically from the ML models."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.ML_FAILURE, details)

class PartialExecutionTrigger(Exception):
    """Raised when ML can only perform degraded execution."""
    pass

def classify_error(e: Exception) -> AIEngineException:
    """
    Deterministic Error Classifier.
    Maps all exceptions to a standardized AIEngineException.
    Guarantees no raw exceptions leak to the contract layer.
    """
    if isinstance(e, AIEngineException):
        return e
    
    if isinstance(e, (ValueError, TypeError, KeyError)):
        return PermanentError(f"Data/Contract Violation: {str(e)}")
        
    if isinstance(e, (ConnectionError, TimeoutError)):
        return TransientError(f"Downstream Connection Issue: {str(e)}")
        
    # Catch-all for unhandled system crashes
    logger.critical(f"UNCLASSIFIED ERROR CAUGHT: {type(e).__name__}: {str(e)}")
    return SystemError(f"Unhandled Internal System Error: {str(e)}")
