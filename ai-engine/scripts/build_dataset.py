import sys
import os

# Ensure project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from app.database.mongo_client import db


def build_dataset(output_path="dataset.npy"):
    print("🔍 Fetching ml_input vectors from Mongo...")

    cursor = db.segments.find({
        "data.ml_input": {"$exists": True}
    })

    vectors = []

    for doc in cursor:
        vector = doc.get("data", {}).get("ml_input")

        if vector and len(vector) == 20:
            vectors.append(vector)

    if not vectors:
        print("❌ No valid vectors found!")
        return

    dataset = np.array(vectors, dtype=np.float32)

    print(f"✅ Dataset shape: {dataset.shape}")

    np.save(output_path, dataset)

    print(f"💾 Dataset saved to: {output_path}")


if __name__ == "__main__":
    build_dataset()