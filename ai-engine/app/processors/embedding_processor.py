def process_embedding(input_ref: str, context: dict):
    return {
        "output_ref": f"{input_ref}_embedding_out" if input_ref else "new_embedding_out",
        "embedding": [1, 2, 3, 4]
    }