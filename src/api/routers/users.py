from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_user
from src.api.schemas.user import UserOut, UserUpdate
from src.database.base import get_db
from src.database.models import User
router = APIRouter(prefix="/api", tags=["Users"])
@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)): return user
@router.patch("/me", response_model=UserOut)
async def update_me(payload: UserUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(user, key, value)
    await db.commit(); await db.refresh(user); return user

