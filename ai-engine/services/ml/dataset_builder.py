import numpy as np
from services.db.mongo_client import get_db

COLLECTION = "segments"

FEATURE_KEYS = [
    "motion_intensity",
    "motion_variance",
    "brightness_avg",
    "flash_count",
    "edge_density_avg",
    "entropy_avg"
]


def build_dataset(limit=None):
    db = get_db()
    collection = db[COLLECTION]

    query = {
        "processing.feature_extraction": "completed"
    }

    cursor = collection.find(query)

    if limit:
        cursor = cursor.limit(limit)

    data = []

    for doc in cursor:
        ps = doc["input_data"]["player_state"]

        vector = [ps.get(k, 0.0) for k in FEATURE_KEYS]
        data.append(vector)

    X = np.array(data, dtype=np.float32)

    print(f"✅ Dataset built: {X.shape}")
    return X


if __name__ == "__main__":
    X = build_dataset()
    np.save("data/dataset.npy", X)
    print("💾 Saved dataset.npy")