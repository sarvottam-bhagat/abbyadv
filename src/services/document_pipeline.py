import hashlib
from uuid import NAMESPACE_URL, uuid5
from qdrant_client.models import PointStruct
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import CaseDocument, DocumentChunk
from src.services.embedding import EmbeddingService
from src.services.qdrant_store import QdrantStore

def chunk_text(text: str, size: int = 1200, overlap: int = 150) -> list[str]:
    text = " ".join(text.split())
    if not text: return []
    chunks=[]; start=0
    while start < len(text):
        end=min(len(text), start+size); chunks.append(text[start:end])
        if end == len(text): break
        start=end-overlap
    return chunks

async def index_document(db: AsyncSession, document: CaseDocument, qdrant: QdrantStore | None = None, embedder: EmbeddingService | None = None) -> int:
    chunks = chunk_text(document.extracted_text or "")
    await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
    qdrant = qdrant or QdrantStore(); embedder = embedder or EmbeddingService(); points=[]
    for index, content in enumerate(chunks):
        chunk_key = f"{document.id}:{index}"; point_id = str(uuid5(NAMESPACE_URL, chunk_key)); vector = await embedder.embed(content)
        record = DocumentChunk(id=point_id, document_id=document.id, user_id=document.user_id, client_id=document.client_id, case_id=document.case_id, chunk_index=index, content=content, content_hash=hashlib.sha256(content.encode()).hexdigest(), vector_id=point_id, metadata_json={"file_name": document.file_name})
        db.add(record); points.append(PointStruct(id=point_id, vector=vector, payload={"document_id":document.id,"user_id":document.user_id,"client_id":document.client_id,"case_id":document.case_id,"chunk_index":index,"content":content,"file_name":document.file_name}))
    await db.commit()
    if points: await qdrant.upsert(points)
    document.embedding_status = "processed"; await db.commit()
    return len(points)
