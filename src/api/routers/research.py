from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.common import get_owned, save
from src.api.deps import get_current_user
from src.api.schemas.research import ResearchIn
from src.database.base import get_db
from src.database.models import Case, ResearchMemo, User
from src.agents.research import ResearchAgent
router = APIRouter(prefix="/api/research", tags=["Research"])
legacy_router = APIRouter(prefix="/api", tags=["Research"])
@router.post("", status_code=201)
async def create(payload: ResearchIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if payload.case_id: await get_owned(db, Case, payload.case_id, user.id)
    result = await ResearchAgent().run(payload.query, user.id, payload.case_id)
    return await save(db, ResearchMemo(user_id=user.id, query=payload.query, client_id=payload.client_id, case_id=payload.case_id, status="success", answer=result["answer"], sources=result["sources"], citations=result["citations"], tool_trace=result["tool_trace"]))
@router.get("/{memo_id}")
async def get(memo_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)): return await get_owned(db, ResearchMemo, memo_id, user.id)
@router.get("/case/{case_id}")
async def list_for_case(case_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await get_owned(db, Case, case_id, user.id); return list((await db.execute(select(ResearchMemo).where(ResearchMemo.case_id == case_id, ResearchMemo.user_id == user.id))).scalars())

@legacy_router.get("/cases/{case_id}/research")
async def list_for_case_legacy(case_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await get_owned(db, Case, case_id, user.id); return list((await db.execute(select(ResearchMemo).where(ResearchMemo.case_id == case_id, ResearchMemo.user_id == user.id))).scalars())
