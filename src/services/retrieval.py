from src.services.embedding import EmbeddingService
from src.services.qdrant_store import QdrantStore
async def retrieve(query: str, user_id: str, case_id: str | None = None, document_id: str | None = None, limit: int = 10):
    filters = {"user_id": user_id}
    if case_id: filters["case_id"] = case_id
    if document_id: filters["document_id"] = document_id
    vector = await EmbeddingService().embed(query)
    return await QdrantStore().search(vector, limit=limit, **filters)

