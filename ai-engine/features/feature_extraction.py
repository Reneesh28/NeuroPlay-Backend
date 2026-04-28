from features.extractors.universal import extract_universal_features
from features.normalization import normalize_features
from features.vector_builder import build_feature_vector

def run_feature_extraction(segment):
    raw = extract_universal_features(segment)
    normalized = normalize_features(raw)
    vector = build_feature_vector(normalized)

    return {
        "features": raw,
        "normalized_features": normalized,
        "ml_input": vector,
        "feature_version": "v1"   # IMPORTANT
    }