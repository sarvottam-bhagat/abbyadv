from src.core.config import get_settings
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue, PayloadSchemaType
class QdrantStore:
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncQdrantClient(url=self.settings.qdrant_url, api_key=self.settings.qdrant_api_key or None)
        self.collection = self.settings.qdrant_collection
    async def ensure_collection(self):
        if not await self.client.collection_exists(self.collection):
            await self.client.create_collection(collection_name=self.collection, vectors_config=VectorParams(size=self.settings.embedding_dimension, distance=Distance.COSINE))
        # Every retrieval is scoped by advocate, and often by matter/document. Qdrant
        # Cloud requires indexes for these filtered searches.
        for field_name in ("user_id", "case_id", "document_id", "client_id"):
            await self.client.create_payload_index(collection_name=self.collection, field_name=field_name, field_schema=PayloadSchemaType.KEYWORD)
    async def search(self, query_vector: list[float], limit: int = 10, **filters):
        await self.ensure_collection()
        conditions = [FieldCondition(key=key, match=MatchValue(value=value)) for key, value in filters.items() if value is not None]
        response = await self.client.query_points(collection_name=self.collection, query=query_vector, query_filter=Filter(must=conditions) if conditions else None, limit=limit, with_payload=True)
        return [{"id": p.id, "score": p.score, "payload": p.payload} for p in response.points]
    async def upsert(self, points: list[PointStruct]):
        await self.ensure_collection(); await self.client.upsert(collection_name=self.collection, points=points); return len(points)
