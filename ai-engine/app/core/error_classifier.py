def classify_error(e: Exception) -> str:
    msg = str(e).lower()

    if "timeout" in msg or "rate" in msg:
        return "TRANSIENT"

    if "json" in msg or "parse" in msg or "empty" in msg:
        return "ML_FAILURE"

    return "UNKNOWN"