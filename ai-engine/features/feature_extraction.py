from features.extractors.universal import extract_universal_features
from features.normalization import normalize_features
from features.vector_builder import build_feature_vector

def run_feature_extraction(segment):
    extraction_result = extract_universal_features(segment)
    
    raw = extraction_result["features"]
    status = extraction_result["status"]
    missing = extraction_result["missing"]

    normalized = normalize_features(raw)
    vector = build_feature_vector(normalized)

    return {
        "features": raw,
        "normalized_features": normalized,
        "ml_input": vector,
        "feature_status": status,      # NEW: diagnostic status
        "missing_features": missing,   # NEW: missing keys
        "feature_version": "v1.1"      # Updated version
    }