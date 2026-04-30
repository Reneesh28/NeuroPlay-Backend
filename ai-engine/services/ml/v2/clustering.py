import os
import numpy as np
import hdbscan
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

# ==============================
# PATHS
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

EMBED_DIR = os.path.join(ROOT_DIR, "embeddings", "v2")
CLUSTER_DIR = os.path.join(ROOT_DIR, "clusters", "v2")

os.makedirs(CLUSTER_DIR, exist_ok=True)


# ==============================
# CLUSTERING PIPELINE
# ==============================
def run_clustering(domain):
    print(f"\n🚀 Clustering for: {domain}")

    embed_path = os.path.join(EMBED_DIR, f"embeddings_{domain}.npy")

    if not os.path.exists(embed_path):
        print("❌ Embeddings not found")
        return

    embeddings = np.load(embed_path)
    print("📊 Embeddings shape:", embeddings.shape)

    # ==============================
    # HDBSCAN
    # ==============================
    print("\n🔹 Running HDBSCAN...")

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=50,
        min_samples=10,
        metric='euclidean'
    )

    labels = clusterer.fit_predict(embeddings)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    noise_ratio = np.sum(labels == -1) / len(labels)

    print(f"Clusters found: {n_clusters}")
    print(f"Noise ratio: {noise_ratio:.2f}")

    # ==============================
    # GMM (only on non-noise)
    # ==============================
    print("\n🔹 Running GMM...")

    valid_mask = labels != -1
    valid_embeddings = embeddings[valid_mask]

    if len(valid_embeddings) == 0:
        print("❌ No valid clusters for GMM")
        return

    gmm = GaussianMixture(
        n_components=n_clusters,
        covariance_type='full',
        random_state=42
    )

    gmm.fit(valid_embeddings)

    # Assign probabilities
    probs = np.zeros((len(embeddings), n_clusters))

    probs[valid_mask] = gmm.predict_proba(valid_embeddings)

    # Confidence = max probability
    confidence = probs.max(axis=1)

    # ==============================
    # EVALUATION
    # ==============================
    print("\n📊 Evaluation:")

    if n_clusters > 1:
        score = silhouette_score(embeddings[valid_mask], labels[valid_mask])
        print("Silhouette score:", round(score, 3))
    else:
        print("Silhouette score: N/A")

    # ==============================
    # PCA VISUALIZATION
    # ==============================
    print("\n📉 Generating PCA plot...")

    pca = PCA(n_components=2)
    reduced = pca.fit_transform(embeddings)

    plt.figure(figsize=(8, 6))
    plt.scatter(
        reduced[:, 0],
        reduced[:, 1],
        c=labels,
        cmap='tab10',
        s=5
    )
    plt.title(f"PCA Clusters - {domain}")
    plt.savefig(os.path.join(CLUSTER_DIR, f"pca_{domain}.png"))
    plt.close()

    print("📸 PCA saved")

    # ==============================
    # SAVE RESULTS
    # ==============================
    cluster_path = os.path.join(CLUSTER_DIR, f"clusters_{domain}.npz")

    np.savez(
        cluster_path,
        labels=labels,
        confidence=confidence
    )

    print(f"💾 Saved → {cluster_path}")


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    domains = ["blackops", "modern_warfare"]

    for d in domains:
        run_clustering(d)