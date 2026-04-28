def extract_universal_features(segment):
    player = segment.get("player_state", {})
    events = segment.get("events", [])

    return {
        "movement_speed": player.get("speed", 0),
        "aim_stability": player.get("accuracy", 0),
        "reaction_time": player.get("reaction_time", 200),

        "engagement_rate": len(events),
        "survival_time": segment.get("timestamp", 0),

        "damage_taken": player.get("damage_taken", 0),
        "damage_dealt": player.get("damage_dealt", 0),

        "accuracy": player.get("accuracy", 0),
        "headshot_rate": player.get("headshot_rate", 0.1),

        "movement_variance": player.get("movement_variance", 0.5),

        # 🔥 NEW FEATURES (20D completion)
        "position_change_rate": player.get("position_change", 1),
        "target_switch_rate": player.get("target_switch", 1),
        "avg_engagement_distance": player.get("distance", 50),

        "cover_usage": player.get("cover_usage", 0.3),
        "reload_frequency": player.get("reloads", 1),

        "kill_streak": player.get("kill_streak", 1),
        "death_rate": player.get("death_rate", 0.2),
        "assist_rate": player.get("assist_rate", 0.3),

        "objective_time": player.get("objective_time", 10),
        "damage_per_second": player.get("dps", 5)
    }