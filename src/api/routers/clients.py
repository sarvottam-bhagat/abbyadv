from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.common import get_owned, save
from src.api.deps import get_current_user
from src.api.schemas.client import ClientIn, ClientOut
from src.database.base import get_db
from src.database.crud import create_client, list_clients
from src.database.models import Client, User

router = APIRouter(prefix="/api/clients", tags=["Clients"])

@router.post("", response_model=ClientOut, status_code=201)
async def create(payload: ClientIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_client(db, user.id, payload.model_dump())

@router.get("", response_model=list[ClientOut])
async def list_all(q: str | None = None, status: str | None = None, limit: int = Query(50, le=100), offset: int = 0, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await list_clients(db, user.id, q, status, limit, offset)

@router.get("/{client_id}", response_model=ClientOut)
async def get(client_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_owned(db, Client, client_id, user.id)

@router.patch("/{client_id}", response_model=ClientOut)
async def update(client_id: str, payload: ClientIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await get_owned(db, Client, client_id, user.id)
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value)
    return await save(db, item)

@router.delete("/{client_id}")
async def archive(client_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await get_owned(db, Client, client_id, user.id); item.status = "archived"; await db.commit(); return {"status": "archived"}

