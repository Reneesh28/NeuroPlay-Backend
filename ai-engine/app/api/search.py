from fastapi import APIRouter
from services.ml.faiss_service import search_similar_segments

router = APIRouter()

@router.post("/search")
async def search(payload: dict):
    try:
        query_embedding = payload.get("embedding")

        if not query_embedding:
            return {
                "status": "error",
                "message": "embedding required"
            }

        result = search_similar_segments(query_embedding)

        return result

    except Exception as e:
        return {
            "status": "fallback",
            "error": str(e)
        }