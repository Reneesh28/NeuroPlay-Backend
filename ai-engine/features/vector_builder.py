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

    # 🔥 NEW FEATURES (to reach 20D)
    "position_change_rate",
    "target_switch_rate",
    "avg_engagement_distance",
    "cover_usage",
    "reload_frequency",
    "kill_streak",
    "death_rate",
    "assist_rate",
    "objective_time",
    "damage_per_second"
]


def build_feature_vector(normalized_features):
    return [normalized_features.get(f, 0.0) for f in FEATURE_ORDER]