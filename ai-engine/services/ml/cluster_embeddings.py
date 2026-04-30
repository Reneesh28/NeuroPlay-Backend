import os
import numpy as np
from sklearn.preprocessing import StandardScaler

# ==============================
# 🔧 PATH CONFIG
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

EMB_PATH = os.path.join(ROOT_DIR, "data", "embeddings.npy")

HDBSCAN_PATH = os.path.join(ROOT_DIR, "data", "clusters_hdbscan.npy")
GMM_PATH = os.path.join(ROOT_DIR, "data", "clusters_gmm.npy")
GMM_PROBA_PATH = os.path.join(ROOT_DIR, "data", "clusters_gmm_proba.npy")

# ==============================
# 🔹 LOAD EMBEDDINGS
# ==============================
X = np.load(EMB_PATH)

# Normalize embeddings
X = StandardScaler().fit_transform(X)

print(f"📦 Loaded embeddings: {X.shape}")

# ==============================
# 🔹 HDBSCAN
# ==============================
import hdbscan

hdbscan_model = hdbscan.HDBSCAN(
    min_cluster_size=200,
    min_samples=20
)

hdb_labels = hdbscan_model.fit_predict(X)

unique, counts = np.unique(hdb_labels, return_counts=True)

print("\n🔷 HDBSCAN")
for u, c in zip(unique, counts):
    print(f"Cluster {u}: {c}")

# ==============================
# 🔹 GMM
# ==============================
from sklearn.mixture import GaussianMixture

gmm_model = GaussianMixture(n_components=6, random_state=42)
gmm_model.fit(X)

gmm_labels = gmm_model.predict(X)
gmm_proba = gmm_model.predict_proba(X)

unique, counts = np.unique(gmm_labels, return_counts=True)

print("\n🔶 GMM")
for u, c in zip(unique, counts):
    print(f"Cluster {u}: {c}")

# ==============================
# 🔹 SAVE RESULTS
# ==============================
np.save(HDBSCAN_PATH, hdb_labels)
np.save(GMM_PATH, gmm_labels)
np.save(GMM_PROBA_PATH, gmm_proba)

print("\n💾 Saved:")
print(f"HDBSCAN → {HDBSCAN_PATH}")
print(f"GMM → {GMM_PATH}")
print(f"GMM Proba → {GMM_PROBA_PATH}")