import os
import numpy as np
import faiss
from sklearn.preprocessing import normalize
from pymongo import MongoClient
from dotenv import load_dotenv
from typing import List, Dict

# ==============================
# 🔹 LOAD ENV
# ==============================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI or not DB_NAME:
    raise ValueError("❌ Missing MONGO_URI or DB_NAME in .env")

# ==============================
# 🔧 PATH CONFIG
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

EMB_PATH = os.path.join(ROOT_DIR, "data", "embeddings.npy")
INDEX_PATH = os.path.join(ROOT_DIR, "data", "faiss.index")

# ==============================
# 🔹 LOAD EMBEDDINGS
# ==============================
if not os.path.exists(EMB_PATH):
    raise FileNotFoundError(f"❌ embeddings.npy not found at {EMB_PATH}")

X = np.load(EMB_PATH).astype("float32")
X = normalize(X)

# ==============================
# 🔹 LOAD FAISS INDEX
# ==============================
if not os.path.exists(INDEX_PATH):
    raise FileNotFoundError(f"❌ faiss.index not found at {INDEX_PATH}")

index = faiss.read_index(INDEX_PATH)

print(f"✅ FAISS loaded | vectors: {index.ntotal}")

# ==============================
# 🔹 CONNECT MONGO
# ==============================
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["segments"]

print("✅ Mongo connected")

# ==============================
# 🔹 BUILD INDEX → DOC MAP
# ==============================
print("📦 Loading segments...")

# Keep ordering stable (VERY IMPORTANT)
segments = list(collection.find({}, {"_id": 0}))

print(f"📊 Loaded {len(segments)} segments")

if len(segments) != len(X):
    raise ValueError(
        f"❌ Mismatch: embeddings={len(X)} vs mongo={len(segments)}"
    )

# ==============================
# 🔹 SEARCH FUNCTION
# ==============================
def search_similar_segments(query_id: int, k: int = 5) -> List[Dict]:
    """
    Returns top-k similar segments
    """

    # 🔥 Validate query
    if query_id < 0 or query_id >= len(X):
        raise ValueError(f"Invalid query_id: {query_id}")

    query_vector = X[query_id].reshape(1, -1)

    scores, indices = index.search(query_vector, k)

    results = []
    seen = set()  # 🔥 remove duplicate indices

    for i in range(k):
        idx = int(indices[0][i])

        # skip duplicates
        if idx in seen:
            continue
        seen.add(idx)

        score = float(scores[0][i])
        segment = segments[idx]

        # 🔥 Optional: lightweight response (recommended)
        results.append({
            "similarity": score,
            "segment": {
                "game_id": segment["game_id"],
                "domain": segment["domain"],
                "session_id": segment["session_id"],
                "start_time_ms": segment["start_time_ms"],
                "end_time_ms": segment["end_time_ms"],
                "sequence_number": segment["sequence_number"],
                "player_state": segment["input_data"]["player_state"]
            }
        })

    return results


# ==============================
# 🔹 TEST
# ==============================
if __name__ == "__main__":
    query_id = 125

    results = search_similar_segments(query_id, k=7)

    print(f"\n🔍 Query ID: {query_id}")
    print("=" * 50)

    for r in results:
        print(f"\nSimilarity: {r['similarity']:.6f}")
        print("Game:", r["segment"]["game_id"])
        print("Time:", r["segment"]["start_time_ms"], "-", r["segment"]["end_time_ms"])