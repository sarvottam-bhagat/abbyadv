from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.common import save
from src.api.deps import get_current_user
from src.api.schemas.event import EventIn
from src.database.base import get_db
from src.database.models import LegalEvent, User
router = APIRouter(prefix="/api/events", tags=["Events"])
@router.post("", status_code=201)
async def create(payload: EventIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)): return await save(db, LegalEvent(user_id=user.id, **payload.model_dump()))
@router.get("")
async def list_all(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)): return list((await db.execute(select(LegalEvent).where(LegalEvent.user_id == user.id).order_by(LegalEvent.event_date))).scalars())

