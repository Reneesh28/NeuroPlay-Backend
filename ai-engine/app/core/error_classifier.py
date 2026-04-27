from enum import Enum
import json

class ErrorCategory(str, Enum):
    TRANSIENT = "TRANSIENT"  # Retryable (e.g., Timeout, Rate Limit)
    ML_FAILURE = "ML_FAILURE"  # Model returned bad data (e.g., Invalid JSON, Empty)
    UNKNOWN = "UNKNOWN"  # System crash

def classify_exception(e: Exception) -> ErrorCategory:
    """
    Classifies an exception into a specific category for handling.
    """
    error_msg = str(e).lower()

    # 🔹 TRANSIENT ERRORS
    if "timeout" in error_msg or "rate limit" in error_msg or "connection" in error_msg:
        return ErrorCategory.TRANSIENT

    # 🔹 ML FAILURES
    if isinstance(e, (json.JSONDecodeError, ValueError, KeyError)):
        return ErrorCategory.ML_FAILURE
    
    if "llm returned none" in error_msg:
        return ErrorCategory.ML_FAILURE

    # 🔹 UNKNOWN ERRORS
    return ErrorCategory.UNKNOWN
