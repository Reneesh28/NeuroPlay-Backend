import numpy as np
import umap
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Cache for projected coordinates to avoid re-calculating
_projection_cache = {}

def project_embeddings_3d(embeddings: np.ndarray, n_neighbors: int = 15, min_dist: float = 0.1) -> np.ndarray:
    """
    Projects high-dimensional embeddings into 3D coordinates using UMAP.
    
    Args:
        embeddings: numpy array of shape (N, D)
        n_neighbors: UMAP parameter for local connectivity
        min_dist: UMAP parameter for how tightly to pack points
        
    Returns:
        numpy array of shape (N, 3)
    """
    try:
        cache_key = f"{embeddings.shape}_{np.sum(embeddings)}"
        if cache_key in _projection_cache:
            logger.info("Serving UMAP projection from cache.")
            return _projection_cache[cache_key]

        logger.info(f"Running UMAP projection for {len(embeddings)} embeddings...")
        reducer = umap.UMAP(
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            n_components=3,
            metric='cosine',
            random_state=42
        )
        embedding_3d = reducer.fit_transform(embeddings)
        _projection_cache[cache_key] = embedding_3d
        return embedding_3d
    except Exception as e:
        logger.error(f"UMAP projection failed: {str(e)}")
        # Fallback to simple PCA if UMAP fails or for very small datasets
        from sklearn.decomposition import PCA
        pca = PCA(n_components=3)
        return pca.fit_transform(embeddings)

def get_domain_embeddings(domain: str) -> Optional[np.ndarray]:
    """Loads raw embeddings for a specific domain."""
    # Logic to find the path (mirroring services.ml.v2.faiss_index)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../"))
    EMBED_DIR = os.path.join(ROOT_DIR, "services", "embeddings", "v2")
    
    # Standardize domain name
    domain = domain.lower().replace(" ", "")
    if domain == "blackops":
        domain = "blackops"
    elif "modern" in domain:
        domain = "modern_warfare"
        
    embed_path = os.path.join(EMBED_DIR, f"embeddings_{domain}.npy")
    
    if os.path.exists(embed_path):
        return np.load(embed_path).astype("float32")
    
    logger.warning(f"Embeddings not found for domain: {domain} at {embed_path}")
    return None
