import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.report.report_agent import ReportAgent
from src.api.common import get_owned, save
from src.api.deps import get_current_user
from src.api.schemas.report import ReportIn
from src.core.config import get_settings
from src.database.base import get_db
from src.database.models import ActionItem, Case, Client, LegalEvent, ReportJob, User
from src.services.storage import StorageService

router = APIRouter(prefix="/api/reports", tags=["Reports"])


def _plain(item) -> dict:
    return {key: value for key, value in item.__dict__.items() if not key.startswith("_")}


async def _build_case_report(db: AsyncSession, case: Case) -> dict:
    actions = (await db.execute(select(ActionItem).where(ActionItem.case_id == case.id).order_by(ActionItem.due_date))).scalars().all()
    events = (await db.execute(select(LegalEvent).where(LegalEvent.case_id == case.id).order_by(LegalEvent.event_date))).scalars().all()
    report = ReportAgent().build_case_summary(_plain(case))
    report["action_items"] = [_plain(item) for item in actions]
    report["events"] = [_plain(event) for event in events]
    report["generated_at"] = datetime.now(timezone.utc).isoformat()
    return report


@router.post("", status_code=201)
async def create(payload: ReportIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if payload.client_id:
        await get_owned(db, Client, payload.client_id, user.id)
    case = await get_owned(db, Case, payload.case_id, user.id) if payload.case_id else None
    job = await save(db, ReportJob(user_id=user.id, client_id=payload.client_id, case_id=payload.case_id, job_type=payload.report_type, status="processing", input_payload=payload.model_dump()))
    try:
        result = await _build_case_report(db, case) if case else {"report_type": payload.report_type, "generated_at": datetime.now(timezone.utc).isoformat()}
        content = json.dumps(result, default=str, indent=2).encode()
        settings = get_settings()
        if settings.supabase_url and settings.supabase_service_role_key:
            key = StorageService().key(user.auth_user_id, payload.case_id or "reports", f"{job.id}.json")
            job.storage_key = await StorageService().upload_bytes(key, content, "application/json")
            job.file_name = f"{job.id}.json"
        job.status = "completed"
        job.result_payload = result
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
    await db.commit()
    await db.refresh(job)
    return job


@router.get("/{job_id}/status")
async def status(job_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_owned(db, ReportJob, job_id, user.id)


@router.get("/{job_id}/download")
async def download(job_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    job = await get_owned(db, ReportJob, job_id, user.id)
    if job.status != "completed":
        raise HTTPException(status_code=409, detail="Report is not completed")
    if not job.storage_key:
        return {"content": job.result_payload, "file_name": job.file_name or f"{job.id}.json"}
    return {"url": await StorageService().signed_download_url(job.storage_key), "file_name": job.file_name}
