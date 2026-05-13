import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict, Any

def identify_clusters(coordinates: np.ndarray, n_clusters: int = 10) -> List[int]:
    """
    Identifies clusters in 3D space.
    
    Args:
        coordinates: (N, 3) array of projected points
        n_clusters: number of clusters to find
        
    Returns:
        List of cluster IDs for each point
    """
    if len(coordinates) < n_clusters:
        return [0] * len(coordinates)
        
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    cluster_ids = kmeans.fit_predict(coordinates)
    return cluster_ids.tolist()

def get_cluster_centers(coordinates: np.ndarray, cluster_ids: List[int]) -> Dict[int, Dict[str, float]]:
    """Calculates the center point of each cluster."""
    centers = {}
    unique_ids = set(cluster_ids)
    
    for cid in unique_ids:
        mask = [i == cid for i in cluster_ids]
        cluster_points = coordinates[mask]
        center = np.mean(cluster_points, axis=0)
        centers[cid] = {
            "x": float(center[0]),
            "y": float(center[1]),
            "z": float(center[2])
        }
        
    return centers
