from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Case, Client

async def create_client(db: AsyncSession, user_id: str, values: dict) -> Client:
    client = Client(user_id=user_id, **values); db.add(client); await db.commit(); await db.refresh(client); return client

async def list_clients(db: AsyncSession, user_id: str, query: str | None, status: str | None, limit: int, offset: int) -> list[Client]:
    stmt = select(Client).where(Client.user_id == user_id).order_by(Client.created_at.desc()).limit(limit).offset(offset)
    if query: stmt = stmt.where(or_(Client.full_name.ilike(f"%{query}%"), Client.email.ilike(f"%{query}%")))
    if status: stmt = stmt.where(Client.status == status)
    return list((await db.execute(stmt)).scalars())

async def create_case(db: AsyncSession, user_id: str, client_id: str, values: dict) -> Case:
    case = Case(user_id=user_id, client_id=client_id, **values); db.add(case); await db.commit(); await db.refresh(case); return case

async def list_cases(db: AsyncSession, user_id: str, client_id: str) -> list[Case]:
    return list((await db.execute(select(Case).where(Case.user_id == user_id, Case.client_id == client_id).order_by(Case.created_at.desc()))).scalars())

