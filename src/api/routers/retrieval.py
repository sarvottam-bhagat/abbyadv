from fastapi import APIRouter, Depends
from src.api.deps import get_current_user
from src.api.schemas.retrieval import RetrievalIn
from src.database.models import User
from src.services.retrieval import retrieve
router = APIRouter(prefix="/api/retrieval", tags=["Retrieval"])
@router.post("/search")
async def search(payload: RetrievalIn, user: User = Depends(get_current_user)):
    return {"results": await retrieve(payload.query, user.id, payload.case_id, payload.document_id, payload.limit)}

