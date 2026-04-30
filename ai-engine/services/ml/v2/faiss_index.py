import os
import numpy as np
import faiss

# ==============================
# PATHS
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

EMBED_DIR = os.path.join(ROOT_DIR, "embeddings", "v2")
DATA_DIR = os.path.join(ROOT_DIR, "data", "v2")
FAISS_DIR = os.path.join(ROOT_DIR, "faiss", "v2")

os.makedirs(FAISS_DIR, exist_ok=True)


# ==============================
# BUILD INDEX (OFFLINE)
# ==============================
def build_faiss_index(domain):
    print(f"\n🚀 Building FAISS index for: {domain}")

    embed_path = os.path.join(EMBED_DIR, f"embeddings_{domain}.npy")
    ids_path = os.path.join(DATA_DIR, f"segment_ids_{domain}.npy")

    if not os.path.exists(embed_path):
        print("❌ Embeddings not found")
        return

    if not os.path.exists(ids_path):
        print("❌ Segment IDs not found (rebuild dataset first)")
        return

    # ------------------------------
    # LOAD DATA
    # ------------------------------
    embeddings = np.load(embed_path).astype("float32")
    segment_ids = np.load(ids_path, allow_pickle=True)

    print("📊 Embedding shape:", embeddings.shape)

    # 🔥 CRITICAL CHECK
    if len(embeddings) != len(segment_ids):
        print("❌ Mismatch detected — STOP")
        print("Embeddings:", len(embeddings))
        print("Segment IDs:", len(segment_ids))
        return

    dim = embeddings.shape[1]

    # ------------------------------
    # BUILD INDEX
    # ------------------------------
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    print(f"✅ Added {index.ntotal} vectors")

    # ------------------------------
    # SAVE INDEX
    # ------------------------------
    index_path = os.path.join(FAISS_DIR, f"faiss_{domain}.index")
    faiss.write_index(index, index_path)

    print(f"💾 Index saved → {index_path}")

    # ------------------------------
    # SAVE MAPPING
    # ------------------------------
    mapping_path = os.path.join(FAISS_DIR, f"mapping_{domain}.npy")
    np.save(mapping_path, segment_ids)

    print(f"💾 Mapping saved → {mapping_path}")


# ==============================
# LOAD INDEX
# ==============================
def load_faiss_index(domain):
    path = os.path.join(FAISS_DIR, f"faiss_{domain}.index")
    return faiss.read_index(path)


# ==============================
# LOAD MAPPING
# ==============================
def load_mapping(domain):
    path = os.path.join(FAISS_DIR, f"mapping_{domain}.npy")
    return np.load(path, allow_pickle=True)


# ==============================
# TEST
# ==============================
def test_faiss(domain):
    print(f"\n🧪 Testing FAISS for: {domain}")

    embed_path = os.path.join(EMBED_DIR, f"embeddings_{domain}.npy")

    embeddings = np.load(embed_path).astype("float32")

    index = load_faiss_index(domain)
    mapping = load_mapping(domain)

    query = embeddings[100]

    distances, indices = index.search(query.reshape(1, -1), 5)

    print("Query index:", 100)
    print("Nearest indices:", indices[0])
    print("Distances:", distances[0])

    print("\n🔗 Segment IDs:")
    for i in indices[0]:
        print(mapping[i])


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    domains = ["blackops", "modern_warfare"]

    for d in domains:
        build_faiss_index(d)

    for d in domains:
        test_faiss(d)