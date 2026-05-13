from fastapi import APIRouter, HTTPException
from app.services.neural_universe.spatial_mapper import map_universe_domain
from app.services.neural_universe.universe_serializer import serialize_universe

router = APIRouter()

@router.get("/map")
async def get_universe_map():
    """
    Returns the full 3D coordinates and links for all domains.
    """
    try:
        blackops_data = map_universe_domain("blackops")
        mw_data = map_universe_domain("modern_warfare")
        
        return serialize_universe(blackops_data, mw_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/domain/{domain_id}")
async def get_domain_map(domain_id: str):
    """
    Returns the 3D map for a specific domain.
    """
    try:
        data = map_universe_domain(domain_id)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
