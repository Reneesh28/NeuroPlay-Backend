from app.pipeline.steps.simulation import run
from app.core.execution_mode import ExecutionMode

# 🔹 Dummy input
input_data = {
    "player_position": "A site",
    "enemy_visible": True,
    "health": 75
}

# 🔹 Dummy context (must match your schema)
context = {
    "user_id": "u1",
    "session_id": "s1",
    "domain": "fps",
    "game_id": "valorant",
    "trace_id": "test-trace-123",
    "feature_version": "v1",
    "pipeline_version": "v1"
}

# 🔹 Run simulation
output, mode = run(
    input_data=input_data,
    context=context,
    execution_mode=ExecutionMode.PARTIAL
)

print("\n=== OUTPUT ===")
print(output)

print("\n=== MODE ===")
print(mode)