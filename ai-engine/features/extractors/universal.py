def extract_universal_features(segment):
    return {
        "movement_speed": segment.get("movement_speed", 0),
        "aim_stability": segment.get("aim_stability", 0),
        "reaction_time": segment.get("reaction_time", 0),
        "engagement_rate": segment.get("engagement_rate", 0),
        "survival_time": segment.get("survival_time", 0),
        "damage_taken": segment.get("damage_taken", 0),
        "damage_dealt": segment.get("damage_dealt", 0),

        "accuracy": segment.get("accuracy", 0),
        "headshot_rate": segment.get("headshot_rate", 0),
        "movement_variance": segment.get("movement_variance", 0),
    }