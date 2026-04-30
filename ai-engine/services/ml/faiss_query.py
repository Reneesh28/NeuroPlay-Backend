import os
import numpy as np
import faiss
from sklearn.preprocessing import normalize

# ==============================
# 🔧 PATH CONFIG
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

EMB_PATH = os.path.join(ROOT_DIR, "data", "embeddings.npy")
INDEX_PATH = os.path.join(ROOT_DIR, "data", "faiss.index")

# ==============================
# 🔹 LOAD DATA
# ==============================
X = np.load(EMB_PATH).astype("float32")

# 🔥 IMPORTANT: normalize (same as index build)
X = normalize(X)

# Load FAISS index
index = faiss.read_index(INDEX_PATH)

print(f"📦 Loaded embeddings: {X.shape}")
print(f"📚 Index size: {index.ntotal}")

# ==============================
# 🔹 QUERY
# ==============================
query_id = 125
query_vector = X[query_id].reshape(1, -1)

k = 5
scores, indices = index.search(query_vector, k)

# ==============================
# 🔹 OUTPUT
# ==============================
print(f"\n🔍 Query ID: {query_id}")
print("Nearest neighbors:")

for i in range(k):
    print(f"ID: {indices[0][i]} | Similarity: {scores[0][i]:.6f}")