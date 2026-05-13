import numpy as np
from typing import List, Dict, Any

def generate_similarity_links(embeddings: np.ndarray, top_k: int = 3, threshold: float = 0.8) -> List[Dict[str, Any]]:
    """
    Generates links between nodes based on embedding similarity.
    
    Args:
        embeddings: Original high-dimensional embeddings
        top_k: Number of neighbors to link to
        threshold: Minimum similarity to create a link
        
    Returns:
        List of link objects: {"source": int, "target": int, "value": float}
    """
    from sklearn.metrics.pairwise import cosine_similarity
    
    # For large datasets, this might be slow. Consider using FAISS index if available.
    # But for a single galaxy (a few thousand nodes), it's manageable.
    sim_matrix = cosine_similarity(embeddings)
    links = []
    
    n = len(embeddings)
    for i in range(n):
        # Get top k indices (excluding self)
        # Partition to get indices of top k+1 elements
        if n <= top_k:
            continue
            
        idx = np.argpartition(sim_matrix[i], -top_k-1)[-top_k-1:]
        # Sort them by similarity
        idx = idx[np.argsort(sim_matrix[i][idx])][::-1]
        
        for j in idx:
            if i == j:
                continue
            
            similarity = float(sim_matrix[i][j])
            if similarity >= threshold:
                links.append({
                    "source": int(i),
                    "target": int(j),
                    "value": similarity
                })
                
    return links
