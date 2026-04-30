from fastapi import APIRouter, Query
from services.ml.faiss_service import search_similar_segments
router = APIRouter()


@router.get("/search/{query_id}")
def search_segments(
    query_id: int,
    k: int = Query(5, ge=1, le=50)
):
    results = search_similar_segments(query_id, k)

    return {
        "query_id": query_id,
        "results": results
    }