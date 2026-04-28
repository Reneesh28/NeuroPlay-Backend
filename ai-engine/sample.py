from app.processors.feature_processor import run
from app.core.execution_mode import ExecutionMode

# 🔹 Minimal dummy input (simulate segment)
sample_input = {
    "events": [],
    "player_state": {
        "speed": 5,
        "accuracy": 0.7
    }
}

# 🔹 Context
context = {
    "trace_id": "test-run",
    "domain": "modern_warfare"
}

# 🔹 Run processor
result, mode = run(sample_input, context, ExecutionMode.FULL)

# 🔹 Output
print("Execution Mode:", mode)
print("ML Input:", result["ml_input"])
print("Vector Length:", len(result["ml_input"]))