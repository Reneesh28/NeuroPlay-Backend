from typing import Dict, Any, List

def serialize_universe(blackops_data: Dict[str, Any], mw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combines domain data into a single universe object for the frontend.
    """
    blackops_count = sum(node.get("count", 1) for node in blackops_data["nodes"])
    mw_count = sum(node.get("count", 1) for node in mw_data["nodes"])

    total_clusters = len(blackops_data["nodes"]) + len(mw_data["nodes"])
    total_edges = len(blackops_data["links"]) + len(mw_data["links"])
    
    spatial_density = 0.0
    if total_clusters > 1:
        spatial_density = (2.0 * total_edges) / (total_clusters * (total_clusters - 1))

    return {
        "status": "success",
        "universe": {
            "nodes": blackops_data["nodes"] + mw_data["nodes"],
            "links": blackops_data["links"] + mw_data["links"],
            "metadata": {
                "blackops_count": blackops_count,
                "mw_count": mw_count,
                "total_nodes": blackops_count + mw_count,
                "spatial_density": round(spatial_density, 3)
            }
        }
    }
