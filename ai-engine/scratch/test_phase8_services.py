import sys
import os
import json
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.profile_schema import PlayerProfile, ProfileSummary
from app.services.profile_updater import compute_profile_update
from app.services.trend_engine import compute_trends
from app.services.memory_weighting import rank_memories
from app.services.pattern_extractor import extract_patterns
from app.services.coaching_engine import generate_coaching

def run_tests():
    print("--- Phase 8 Validation Test ---")
    
    # 1. Profile Updater
    print("\n[1] Testing profile_updater...")
    profile_summary = ProfileSummary(user_id="test_user", version=1)
    profile_dict = profile_summary.model_dump()
    # mock simulation result
    sim_result = {
        "execution_mode": "tactical",
        "predicted_action": "push aggressively",
        "reasoning": "The enemy is weak, I should attack.",
        "confidence": 0.8
    }
    update = compute_profile_update(profile_dict, sim_result, {"memory": [{"cluster_id": 5}]})
    print("Update Payload:", json.dumps(update, indent=2, default=str))
    assert "aggression_score" in update
    
    # 2. Trend Engine
    print("\n[2] Testing trend_engine...")
    snapshots = [
        {"aggression_score": 0.5, "adaptability_score": 0.5},
        {"aggression_score": 0.6, "adaptability_score": 0.5},
        {"aggression_score": 0.7, "adaptability_score": 0.6}
    ]
    trends = compute_trends(snapshots)
    print("Trends:", json.dumps(trends, indent=2))
    assert "aggression_trend" in trends
    
    # 3. Memory Weighting
    print("\n[3] Testing memory_weighting...")
    memories = [
        {"distance": 0.1, "timestamp": datetime.now().isoformat(), "metadata": {"confidence": 0.8, "outcome_success": True}},
        {"distance": 0.9, "timestamp": "2023-01-01T00:00:00", "metadata": {"confidence": 0.2, "outcome_success": False}}
    ]
    ranked = rank_memories(memories, "cluster_5")
    print("Ranked Memories Count:", len(ranked))
    assert len(ranked) > 0
    
    # 4. Pattern Extractor
    print("\n[4] Testing pattern_extractor...")
    full_profile = PlayerProfile(
        user_id="test_user",
        cluster_distribution={"5": 10, "1": 2},
        reaction_profile={"avg_response_time": 1.5, "consistency_score": 0.4, "under_pressure_score": 0.3},
        aggression_score=0.9,
        adaptability_score=0.2
    )
    patterns = extract_patterns(memories, full_profile.model_dump())
    print("Extracted Patterns:", json.dumps(patterns, indent=2))
    assert "strengths" in patterns
    
    # 5. Coaching Engine
    print("\n[5] Testing coaching_engine...")
    coaching = generate_coaching(full_profile.model_dump(), trends, patterns)
    print("Coaching Tips:", json.dumps(coaching, indent=2))
    assert isinstance(coaching, list)

    print("\n[OK] All tests passed successfully!")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
