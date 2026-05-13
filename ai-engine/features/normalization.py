import logging
import math

logger = logging.getLogger(__name__)

FEATURE_RANGES = {
    "movement_speed": (0, 10),
    "aim_stability": (0, 1),
    "reaction_time": (0, 500),
    "engagement_rate": (0, 10),
    "survival_time": (0, 300),
    "damage_taken": (0, 200),
    "damage_dealt": (0, 200),
    "accuracy": (0, 1),
    "headshot_rate": (0, 1),
    "movement_variance": (0, 5),

    # new features (for 20D)
    "position_change_rate": (0, 10),
    "target_switch_rate": (0, 10),
    "avg_engagement_distance": (0, 100),
    "cover_usage": (0, 1),
    "reload_frequency": (0, 10),
    "kill_streak": (0, 20),
    "death_rate": (0, 10),
    "assist_rate": (0, 10),
    "objective_time": (0, 300),
    "damage_per_second": (0, 50),
}


def normalize_features(features):
    normalized = {}

    for key, value in features.items():
        try:
            # 1. Type Enforcement
            val = float(value) if value is not None else 0.0
            
            # 2. NaN / Infinity Protection
            if math.isnan(val) or math.isinf(val):
                logger.warning(f"Corrupted telemetry detected: {key}={val}. Resetting to 0.0")
                val = 0.0

            min_val, max_val = FEATURE_RANGES.get(key, (0, 1))

            if max_val - min_val == 0:
                norm = 0.0
            else:
                norm = (val - min_val) / (max_val - min_val)

            # 3. Range Clamping
            normalized[key] = max(0.0, min(1.0, norm))

        except (ValueError, TypeError) as e:
            logger.error(f"Normalization failed for {key}: {str(e)}")
            normalized[key] = 0.0

    return normalized