def process_simulation(input_ref: str, context: dict):
    return {
        "output_ref": f"{input_ref}_simulation_out" if input_ref else "new_simulation_out",
        "result": "simulation complete"
    }