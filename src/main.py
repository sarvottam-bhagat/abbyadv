from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from src.core.config import get_settings
from src.database.base import init_db
from src.core.logging import RequestIdMiddleware, configure_logging
from src.api.routers.users import router as users_router
from src.api.routers.clients import router as clients_router
from src.api.routers.cases import router as cases_router
from src.api.routers.documents import router as documents_router
from src.api.routers.chat import router as chat_router
from src.api.routers.scenarios import router as scenarios_router, legacy_router as scenarios_legacy_router
from src.api.routers.drafts import router as drafts_router
from src.api.routers.research import router as research_router, legacy_router as research_legacy_router
from src.api.routers.events import router as events_router
from src.api.routers.dashboard import router as dashboard_router
from src.api.routers.parties import router as parties_router
from src.api.routers.action_items import router as action_items_router
from src.api.routers.reports import router as reports_router
from src.api.routers.retrieval import router as retrieval_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_production()
    if settings.debug or settings.auto_create_schema: await init_db()
    yield

settings=get_settings()
configure_logging()
app=FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list if not settings.debug else ["*"], allow_credentials=True, allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"], allow_headers=["Authorization", "Content-Type", "X-User-Id"])
for api_router in (users_router, clients_router, cases_router, documents_router, chat_router, scenarios_router, scenarios_legacy_router, drafts_router, research_router, research_legacy_router, events_router, dashboard_router, parties_router, action_items_router, reports_router, retrieval_router):
    app.include_router(api_router)

@app.get("/health")
async def health(): return {"status":"ok"}

@app.get("/ready")
async def ready():
    from src.database.base import engine
    try:
        async with engine.connect() as connection: await connection.execute(text("SELECT 1"))
        return {"status":"ready", "database":"ok"}
    except Exception:
        return JSONResponse(status_code=503, content={"status":"not_ready", "database":"error", "error":"database unavailable"})

@app.get("/")
async def root(): return {"message":"AbbyAdv API is live"}
