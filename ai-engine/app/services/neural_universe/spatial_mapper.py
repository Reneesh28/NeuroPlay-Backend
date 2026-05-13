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
    
    # 3. Apply Domain Offset
    offset = get_domain_offset(domain)
    nodes = []
    for i, coord in enumerate(coords_3d):
        orig_idx = int(indices[i])
        nodes.append({
            "id": f"{domain}_{orig_idx}",
            "domain": domain,
            "x": float(coord[0] + offset[0]),
            "y": float(coord[1] + offset[1]),
            "z": float(coord[2] + offset[2]),
            "confidence": 0.9, # Placeholder for actual confidence
            "memory_strength": 0.8 # Placeholder
        })
        
    # 4. Identify Clusters
    cluster_ids = identify_clusters(coords_3d)
    for i, node in enumerate(nodes):
        node["cluster_id"] = int(cluster_ids[i])
        
    # 5. Generate Links
    links = generate_similarity_links(embeddings_subset)
    # Remap link indices to node IDs
    formatted_links = []
    for link in links:
        formatted_links.append({
            "source": nodes[link["source"]]["id"],
            "target": nodes[link["target"]]["id"],
            "value": link["value"]
        })
        
    return {
        "domain": domain,
        "nodes": nodes,
        "links": formatted_links
    }
