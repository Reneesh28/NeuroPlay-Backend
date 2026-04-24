from app.models.llm_loader import call_llm
from app.prompting.templates import build_simulation_prompt
from app.utils.output_parser import parse_llm_output

input_data = {
    "situation": "1v2 clutch",
    "ammo": "low",
    "enemy_direction": "left"
}

context = {
    "player_type": "aggressive",
    "game": "valorant"
}

prompt = build_simulation_prompt(input_data, context)

raw_response = call_llm(prompt)

parsed = parse_llm_output(raw_response)

print("\n=== PARSED OUTPUT ===\n")
print(parsed)