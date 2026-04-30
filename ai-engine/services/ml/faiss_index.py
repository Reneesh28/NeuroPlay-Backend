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
# 🔹 LOAD EMBEDDINGS
# ==============================
X = np.load(EMB_PATH).astype("float32")

print(f"📦 Loaded embeddings: {X.shape}")

# ==============================
# 🔹 NORMALIZE (CRITICAL)
# ==============================
X = normalize(X)   # L2 normalization

# Optional: tiny noise to break exact duplicates
# X += 1e-6 * np.random.randn(*X.shape).astype("float32")

# ==============================
# 🔹 BUILD FAISS INDEX (COSINE)
# ==============================
dim = X.shape[1]

# 🔥 Use Inner Product for cosine similarity
index = faiss.IndexFlatIP(dim)

index.add(X)

print(f"✅ FAISS index built: {index.ntotal} vectors")

# ==============================
# 🔹 SAVE INDEX
# ==============================
faiss.write_index(index, INDEX_PATH)

print(f"💾 Saved FAISS index → {INDEX_PATH}")