from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.common import get_owned, save
from src.api.deps import get_current_user
from src.api.schemas.action_item import ActionItemIn
from src.database.base import get_db
from src.database.models import ActionItem, Case, User
router = APIRouter(prefix="/api/action-items", tags=["Action Items"])
@router.post("", status_code=201)
async def create(payload: ActionItemIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if payload.case_id: await get_owned(db, Case, payload.case_id, user.id)
    return await save(db, ActionItem(user_id=user.id, **payload.model_dump()))
@router.get("")
async def list_all(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)): return list((await db.execute(select(ActionItem).where(ActionItem.user_id == user.id).order_by(ActionItem.due_date))).scalars())
@router.patch("/{item_id}")
async def update(item_id: str, payload: ActionItemIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await get_owned(db, ActionItem, item_id, user.id)
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value)
    return await save(db, item)

