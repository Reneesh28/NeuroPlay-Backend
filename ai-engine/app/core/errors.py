from enum import Enum
from typing import Dict, Any, Optional

class ErrorType(str, Enum):
    TRANSIENT = "TRANSIENT"
    SYSTEM = "SYSTEM"
    PERMANENT = "PERMANENT"

class AIEngineException(Exception):
    """Base exception for all AI Engine errors."""
    def __init__(self, message: str, error_type: ErrorType, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details or {}

class TransientError(AIEngineException):
    """Errors that can be retried (e.g., timeouts, temporary DB issues)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.TRANSIENT, details)

class SystemError(AIEngineException):
    """Internal system errors (e.g., memory overflow, unexpected crashes)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.SYSTEM, details)

class PermanentError(AIEngineException):
    """Errors that should NOT be retried (e.g., invalid schema, missing domain)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.PERMANENT, details)

class PartialExecutionTrigger(Exception):
    """Raised when the ML model detects it can only perform a degraded/partial execution."""
    pass
