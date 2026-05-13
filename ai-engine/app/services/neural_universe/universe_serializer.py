from typing import Dict, Any, List

def serialize_universe(blackops_data: Dict[str, Any], mw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combines domain data into a single universe object for the frontend.
    """
    return {
        "status": "success",
        "universe": {
            "nodes": blackops_data["nodes"] + mw_data["nodes"],
            "links": blackops_data["links"] + mw_data["links"],
            "metadata": {
                "blackops_count": len(blackops_data["nodes"]),
                "mw_count": len(mw_data["nodes"]),
                "total_nodes": len(blackops_data["nodes"]) + len(mw_data["nodes"])
            }
        }
    }
