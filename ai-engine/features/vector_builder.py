FEATURE_ORDER = [
    "movement_speed",
    "aim_stability",
    "reaction_time",
    "engagement_rate",
    "survival_time",
    "damage_taken",
    "damage_dealt",
    "accuracy",
    "headshot_rate",
    "movement_variance",
]

def build_feature_vector(normalized_features):
    return [normalized_features.get(f, 0.0) for f in FEATURE_ORDER]