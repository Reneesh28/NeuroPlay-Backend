import sys
import os

# Ensure project root is available
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
import random
from uuid import uuid4

from app.database.mongo_client import db

URL = "http://localhost:8000/ai/execute"


def generate_segment():
    return {
        "events": random.choices(
            ["move", "shoot", "reload"],
            k=random.randint(1, 5)
        ),
        "player_state": {
            "speed": random.uniform(1, 10),
            "accuracy": random.uniform(0.3, 1.0),
            "damage_dealt": random.uniform(10, 100),
            "damage_taken": random.uniform(0, 50)
        },
        "timestamp": random.uniform(1, 300)
    }


def insert_segment(i):
    # 🔥 Generate UNIQUE REF
    ref = f"seg_{i}_{uuid4().hex[:6]}"

    doc = {
        "ref": ref,
        "domain": "modern_warfare",
        "input_data": generate_segment()
    }

    db.segments.insert_one(doc)

    return ref  # 🔥 CRITICAL

def call_api(i, ref):
    payload = {
        "job_id": f"job_{i}",
        "step": "feature_extraction",
        "input_ref": ref,
        "input_type": "segment",
        "context": {
            "user_id": "user1",
            "session_id": "sess1",
            "domain": "modern_warfare",
            "game_id": "mw2",
            "trace_id": f"trace_{i}",
            "feature_version": "v1",
            "pipeline_version": "v1",
            "resolved_model_version": "v1"
        }
    }

    # 🔥 STEP 1: Feature extraction
    response = requests.post(URL, json=payload)
    result = response.json()

    print("FEATURE:", i, response.status_code, result)

    feature_ref = result.get("output_ref")

    # 🔥 STEP 2: Embedding generation
    embed_payload = {
        "job_id": f"job_embed_{i}",
        "step": "embedding_generation",
        "input_ref": feature_ref,
        "input_type": "feature",
        "context": payload["context"]
    }

    embed_response = requests.post(URL, json=embed_payload)

    print("EMBED:", i, embed_response.status_code, embed_response.text)


if __name__ == "__main__":
    for i in range(50):
        ref = insert_segment(i)   # 🔥 get correct ref
        call_api(i, ref)          # 🔥 pass same ref