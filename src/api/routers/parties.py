from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.common import get_owned, save
from src.api.deps import get_current_user
from src.api.schemas.party import PartyIn
from src.database.base import get_db
from src.database.models import Case, CaseParty, User
router = APIRouter(prefix="/api", tags=["Case Parties"])
@router.post("/cases/{case_id}/parties", status_code=201)
async def create(case_id: str, payload: PartyIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await get_owned(db, Case, case_id, user.id); return await save(db, CaseParty(case_id=case_id, **payload.model_dump()))
@router.get("/cases/{case_id}/parties")
async def list_for_case(case_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await get_owned(db, Case, case_id, user.id); return list((await db.execute(select(CaseParty).where(CaseParty.case_id == case_id))).scalars())

