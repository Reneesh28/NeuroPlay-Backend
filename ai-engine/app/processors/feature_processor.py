def process_feature(input_ref: str, context: dict):
    return {
        "output_ref": f"{input_ref}_feature_out" if input_ref else "new_feature_out",
        "features": [0.2, 0.4, 0.8],
        "status": "feature extraction complete"
    }