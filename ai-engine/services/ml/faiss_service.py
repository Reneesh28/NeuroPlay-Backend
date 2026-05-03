import os
import numpy as np

# ==============================
# PATH CONFIG
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

DATA_DIR = os.path.join(ROOT_DIR, "data")
EMB_PATH = os.path.join(DATA_DIR, "embeddings.npy")

# ==============================
# LAZY LOAD EMBEDDINGS
# ==============================
def get_embeddings():
    if not os.path.exists(EMB_PATH):
        print(f"⚠️ embeddings.npy not found at {EMB_PATH}")
        return None
    return np.load(EMB_PATH)


# ==============================
# SEARCH FUNCTION (SAFE)
# ==============================
def search_similar_segments(query_embedding, top_k=5):
    embeddings = get_embeddings()

    if embeddings is None:
        return {
            "status": "fallback",
            "results": [],
            "message": "FAISS data not available"
        }

    try:
        # simple similarity (replace later with FAISS index if needed)
        similarities = np.dot(embeddings, query_embedding)

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            results.append({
                "index": int(idx),
                "score": float(similarities[idx])
            })

        return {
            "status": "success",
            "results": results
        }

    except Exception as e:
        return {
            "status": "fallback",
            "results": [],
            "error": str(e)
        }