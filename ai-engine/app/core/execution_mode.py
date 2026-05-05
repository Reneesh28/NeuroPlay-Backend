import traceback
import logging
from typing import Callable, Any, Tuple, Dict
from app.core.errors import SystemError

logger = logging.getLogger(__name__)


class ExecutionMode:
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    FALLBACK = "FALLBACK"

def detect_ml_failure(error: Exception) -> str:
    """
    Detects if the failure should degrade to PARTIAL or completely FALLBACK.
    """
    msg = str(error).lower()
    
    # ML Degradation (e.g., poor parse, missing data, timeouts) -> PARTIAL
    if any(k in msg for k in ["timeout", "json", "parse", "empty", "schema", "degraded", "llm"]):
        return ExecutionMode.PARTIAL
        
    # Catastrophic failure -> FALLBACK
    return ExecutionMode.FALLBACK