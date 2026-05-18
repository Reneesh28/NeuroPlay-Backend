import numpy as np
import logging
from typing import Dict, Any, List

from .dimensionality_reduction import project_embeddings_3d, get_domain_embeddings
from .domain_separator import get_domain_offset
from .cluster_projection import identify_clusters
from .similarity_links import generate_similarity_links

logger = logging.getLogger(__name__)

def map_universe_domain(domain: str) -> Dict[str, Any]:
    """
    Coordinates the full mapping of a single domain galaxy.
    """
    # 1. Load Embeddings
    embeddings = get_domain_embeddings(domain)
    if embeddings is None:
        return {"nodes": [], "links": [], "clusters": {}}
        
    # 2. Project to 3D
    # Limit to 2000 nodes for performance if needed, but the requirement says thousands
    # Let's try full set first or a reasonable subset
    max_nodes = 2000 
    if len(embeddings) > max_nodes:
        logger.info(f"Subsampling {len(embeddings)} to {max_nodes} for performance.")
        indices = np.random.choice(len(embeddings), max_nodes, replace=False)
        embeddings_subset = embeddings[indices]
    else:
        indices = np.arange(len(embeddings))
        embeddings_subset = embeddings
        
    coords_3d = project_embeddings_3d(embeddings_subset)
    
    # 3. Identify Clusters
    cluster_ids = identify_clusters(coords_3d)
    
    # Calculate cluster centers
    from .cluster_projection import get_cluster_centers
    centers = get_cluster_centers(coords_3d, cluster_ids)
    
    # Count members in each cluster
    counts = {}
    for cid in cluster_ids:
        counts[cid] = counts.get(cid, 0) + 1
        
    # 4. Apply Domain Offset and Scaling
    offset = get_domain_offset(domain)
    scale = 8.0 # Expand projection
    
    cluster_nodes = []
    for cid, center in centers.items():
        cluster_nodes.append({
            "id": f"{domain}_{cid}",
            "domain": domain,
            "cluster_id": cid,
            "x": float((center["x"] * scale) + offset[0]),
            "y": float((center["y"] * scale) + offset[1]),
            "z": float((center["z"] * scale) + offset[2]),
            "confidence": 0.9,
            "memory_strength": 0.8,
            "count": counts[cid],
            "isCluster": True
        })
        
    # 5. Aggregate Links between Clusters
    raw_links = generate_similarity_links(embeddings_subset)
    cluster_links_map = {}
    
    for link in raw_links:
        s_idx = link["source"]
        t_idx = link["target"]
        s_cid = cluster_ids[s_idx]
        t_cid = cluster_ids[t_idx]
        
        if s_cid != t_cid:
            key = tuple(sorted([s_cid, t_cid]))
            if key not in cluster_links_map:
                cluster_links_map[key] = 0
            cluster_links_map[key] += link["value"]
            
    formatted_links = []
    for (s_cid, t_cid), value in cluster_links_map.items():
        formatted_links.append({
            "source": f"{domain}_{s_cid}",
            "target": f"{domain}_{t_cid}",
            "value": float(value)
        })
        
    return {
        "domain": domain,
        "nodes": cluster_nodes,
        "links": formatted_links
    }
