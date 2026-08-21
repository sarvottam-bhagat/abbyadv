from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.common import get_owned, save
from src.api.deps import get_current_user
from src.api.schemas.case import CaseIn, CaseOut
from src.database.base import get_db
from src.database.crud import create_case, list_cases
from src.database.models import Case, Client, User

router = APIRouter(prefix="/api", tags=["Cases"])

@router.post("/clients/{client_id}/cases", response_model=CaseOut, status_code=201)
async def create(client_id: str, payload: CaseIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await get_owned(db, Client, client_id, user.id)
    return await create_case(db, user.id, client_id, payload.model_dump())

@router.get("/clients/{client_id}/cases", response_model=list[CaseOut])
async def list_for_client(client_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await get_owned(db, Client, client_id, user.id); return await list_cases(db, user.id, client_id)

@router.get("/cases/{case_id}", response_model=CaseOut)
async def get(case_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_owned(db, Case, case_id, user.id)

@router.patch("/cases/{case_id}", response_model=CaseOut)
async def update(case_id: str, payload: CaseIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await get_owned(db, Case, case_id, user.id)
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value)
    return await save(db, item)

@router.delete("/cases/{case_id}")
async def archive(case_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await get_owned(db, Case, case_id, user.id); item.case_status = "archived"; await db.commit(); return {"status": "archived"}

