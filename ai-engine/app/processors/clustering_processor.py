def process_clustering(input_ref: str, context: dict):
    return {
        "output_ref": f"{input_ref}_clustering_out" if input_ref else "new_clustering_out",
        "clusters": [0, 1, 1, 0]
    }