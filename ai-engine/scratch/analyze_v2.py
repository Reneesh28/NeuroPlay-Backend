import os
import numpy as np

base_dir = r"C:\Users\Bloodblade\Desktop\PROJECTS\NeuroPlay\core-backend\ai-engine\services"
domain = "blackops"

dataset_path = os.path.join(base_dir, "data", "v2", f"dataset_{domain}.npy")
embed_path = os.path.join(base_dir, "embeddings", "v2", f"embeddings_{domain}.npy")
cluster_path = os.path.join(base_dir, "clusters", "v2", f"clusters_{domain}.npz")

X = np.load(dataset_path)
embeddings = np.load(embed_path)
clusters = np.load(cluster_path)
labels = clusters['labels']

print(f"Domain: {domain}")
print(f"Dataset shape: {X.shape}")
print(f"Embeddings shape: {embeddings.shape}")
print(f"Labels shape: {labels.shape}")

unique_labels, counts = np.unique(labels, return_counts=True)
print(f"\nClusters found: {len(unique_labels)}")
for l, c in zip(unique_labels, counts):
    print(f"Cluster {l}: {c} points")

# Let's check average feature values for each cluster
# Features:
feature_names = [
    "motion", "variance", "brightness", "flash", "edge", "entropy",
    "motion/var", "1/var", "bright*edge", "entropy*motion", "flash/5",
    "motion*bright", "edge*entropy", "motion*entropy", "motion^2", "entropy^2",
    "diff_motion", "diff_entropy", "pad1", "pad2"
]

print("\nCluster Analysis (Average Features):")
for cluster_id in unique_labels:
    if cluster_id == -1:
        continue # skip noise for now, or just print it if we want
    mask = labels == cluster_id
    cluster_data = X[mask]
    mean_features = np.mean(cluster_data, axis=0)
    
    print(f"\n--- Cluster {cluster_id} ---")
    # print top 3 highest features (relative to overall mean)
    # let's just print the main raw features
    main_features_idx = [0, 1, 2, 3, 4, 5]
    for idx in main_features_idx:
        print(f"  {feature_names[idx]}: {mean_features[idx]:.4f}")
