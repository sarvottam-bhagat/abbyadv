from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_owned(db: AsyncSession, model, item_id: str, user_id: str):
    item = (await db.execute(select(model).where(model.id == item_id, model.user_id == user_id))).scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return item

async def save(db: AsyncSession, item):
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

