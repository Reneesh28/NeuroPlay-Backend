import logging

logger = logging.getLogger(__name__)

def extract_universal_features(segment: dict) -> dict:
    """
    Safely extracts telemetry features with status tracking.
    Prevents silent failures by classifying missing vs zero data.
    """
    player = segment.get("player_state", {})
    events = segment.get("events", [])
    
    feature_status = {}
    missing_features = []
    features = {}

    def safe_extract(key: str, source: dict, feature_name: str, default_val: float) -> float:
        if key in source:
            val = source[key]
            if val is not None:
                feature_status[feature_name] = "computed"
                try:
                    return float(val)
                except (ValueError, TypeError):
                    feature_status[feature_name] = "invalid_value"
                    return default_val
        
        missing_features.append(key)
        feature_status[feature_name] = "missing_source"
        return default_val

    # --- Movement Metrics ---
    # Primary: "speed" | Fallback: "motion_intensity"
    features["movement_speed"] = safe_extract("speed", player, "movement_speed", 0.0)
    if feature_status["movement_speed"] == "missing_source" and "motion_intensity" in player:
        features["movement_speed"] = float(player["motion_intensity"])
        feature_status["movement_speed"] = "computed_cv_fallback"

    features["aim_stability"] = safe_extract("accuracy", player, "aim_stability", 0.0)
    features["reaction_time"] = safe_extract("reaction_time", player, "reaction_time", 200.0)
    
    # --- Engagement Metrics ---
    features["engagement_rate"] = float(len(events))
    feature_status["engagement_rate"] = "computed"
    
    features["survival_time"] = float(segment.get("timestamp", 0.0))
    feature_status["survival_time"] = "computed"
    
    # --- Combat Metrics ---
    features["damage_taken"] = safe_extract("damage_taken", player, "damage_taken", 0.0)
    features["damage_dealt"] = safe_extract("damage_dealt", player, "damage_dealt", 0.0)
    
    # Advanced Accuracy Logic (Derived vs Direct)
    shots = player.get("shots_fired")
    hits = player.get("hits")
    if shots is not None and hits is not None and float(shots) > 0:
        features["accuracy"] = float(hits) / float(shots)
        feature_status["accuracy"] = "computed"
    else:
        features["accuracy"] = safe_extract("accuracy", player, "accuracy", 0.0)

    features["headshot_rate"] = safe_extract("headshot_rate", player, "headshot_rate", 0.1)

    # Movement Variance: Primary: "movement_variance" | Fallback: "motion_variance"
    features["movement_variance"] = safe_extract("movement_variance", player, "movement_variance", 0.5)
    if feature_status["movement_variance"] == "missing_source" and "motion_variance" in player:
        features["movement_variance"] = float(player["motion_variance"])
        feature_status["movement_variance"] = "computed_cv_fallback"

    # --- 20D Completion Features ---
    # Fallback mappings for event-derived features
    features["position_change_rate"] = safe_extract("position_change", player, "position_change_rate", 1.0)
    features["target_switch_rate"] = safe_extract("target_switch", player, "target_switch_rate", 1.0)
    features["avg_engagement_distance"] = safe_extract("distance", player, "avg_engagement_distance", 50.0)
    
    features["cover_usage"] = safe_extract("cover_usage", player, "cover_usage", 0.3)
    features["reload_frequency"] = safe_extract("reloads", player, "reload_frequency", 1.0)
    
    features["kill_streak"] = safe_extract("kill_streak", player, "kill_streak", 1.0)
    features["death_rate"] = safe_extract("death_rate", player, "death_rate", 0.2)
    features["assist_rate"] = safe_extract("assist_rate", player, "assist_rate", 0.3)
    
    features["objective_time"] = safe_extract("objective_time", player, "objective_time", 10.0)
    features["damage_per_second"] = safe_extract("dps", player, "damage_per_second", 5.0)

    # Final diagnostic check: if engagement_rate > 0 but core combat is 0, check events
    if features["engagement_rate"] > 0 and features["damage_dealt"] == 0:
        # Check if events list contains damage-like objects
        damage_events = [e for e in events if isinstance(e, dict) and "damage" in e.get("type", "").lower()]
        if damage_events:
            total_damage = sum(float(e.get("value", 0)) for e in damage_events)
            features["damage_dealt"] = total_damage
            feature_status["damage_dealt"] = "computed_event_sum"

    # NEW: Structured Return for Diagnostic Visibility
    return {
        "features": features,
        "status": feature_status,
        "missing": missing_features
    }
