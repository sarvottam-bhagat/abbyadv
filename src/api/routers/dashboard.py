from fastapi import APIRouter, Depends
from datetime import date, timedelta
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_user
from src.database.base import get_db
from src.database.models import ActionItem, Case, CaseDocument, Client, Draft, LegalEvent, LegalScenario, User
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def _date(value: date | None) -> str | None:
    return value.isoformat() if value else None


@router.get("/summary")
async def summary(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    today = date.today(); week_end = today + timedelta(days=6); next_month = today + timedelta(days=30)
    clients = await db.scalar(select(func.count(Client.id)).where(Client.user_id == user.id)); cases = await db.scalar(select(func.count(Case.id)).where(Case.user_id == user.id, Case.case_status == "active")); drafts = await db.scalar(select(func.count(Draft.id)).where(Draft.user_id == user.id, Draft.status == "draft")); docs = await db.scalar(select(func.count(CaseDocument.id)).where(CaseDocument.user_id == user.id, CaseDocument.processing_status != "processed"))
    ready_docs = await db.scalar(select(func.count(CaseDocument.id)).where(CaseDocument.user_id == user.id, CaseDocument.processing_status == "processed"))
    hearings = await db.scalar(select(func.count(LegalEvent.id)).where(LegalEvent.user_id == user.id, LegalEvent.event_type.in_(["hearing", "court_date"]), LegalEvent.event_date.between(today, week_end), LegalEvent.status == "active"))
    critical = await db.scalar(select(func.count(ActionItem.id)).where(ActionItem.user_id == user.id, ActionItem.priority.in_(["critical", "high"]), ActionItem.status == "active"))
    scenarios = await db.scalar(select(func.count(LegalScenario.id)).where(LegalScenario.user_id == user.id, LegalScenario.execution_status == "success"))

    active_cases = (await db.execute(select(Case).where(Case.user_id == user.id, Case.case_status == "active").order_by(Case.updated_at.desc()).limit(4))).scalars().all()
    active_case_ids = [case.id for case in active_cases]
    case_clients = {client.id: client.full_name for client in (await db.execute(select(Client).where(Client.user_id == user.id))).scalars().all()}
    case_document_counts: dict[str, int] = {}
    if active_case_ids:
        rows = await db.execute(select(CaseDocument.case_id, func.count(CaseDocument.id)).where(CaseDocument.case_id.in_(active_case_ids)).group_by(CaseDocument.case_id))
        case_document_counts = {case_id: count for case_id, count in rows.all() if case_id}

    focus_items = (await db.execute(select(ActionItem).where(ActionItem.user_id == user.id, ActionItem.status == "active").order_by(ActionItem.priority.desc(), ActionItem.due_date.asc().nulls_last()).limit(4))).scalars().all()
    upcoming_events = (await db.execute(select(LegalEvent).where(LegalEvent.user_id == user.id, LegalEvent.status == "active", LegalEvent.event_date.between(today, next_month)).order_by(LegalEvent.event_date).limit(4))).scalars().all()
    case_names = {case.id: case.case_name for case in active_cases}
    for item in [*focus_items, *upcoming_events]:
        if item.case_id and item.case_id not in case_names:
            case = await db.get(Case, item.case_id)
            if case and case.user_id == user.id:
                case_names[case.id] = case.case_name

    recent_drafts = (await db.execute(select(Draft).where(Draft.user_id == user.id).order_by(Draft.updated_at.desc()).limit(2))).scalars().all()
    recent_scenarios = (await db.execute(select(LegalScenario).where(LegalScenario.user_id == user.id).order_by(LegalScenario.updated_at.desc()).limit(2))).scalars().all()
    activity = []
    activity.extend({"kind": "draft", "title": draft.title, "detail": "Draft ready for review", "date": draft.updated_at.isoformat(), "case_id": draft.case_id} for draft in recent_drafts)
    activity.extend({"kind": "scenario", "title": scenario.name, "detail": "Scenario analysis completed" if scenario.execution_status == "success" else "Scenario analysis in progress", "date": scenario.updated_at.isoformat(), "case_id": scenario.case_id} for scenario in recent_scenarios)
    activity.extend({"kind": "case", "title": case.case_name, "detail": f"{case_clients.get(case.client_id, 'Client')} · {case.current_stage or 'Active matter'}", "date": case.updated_at.isoformat(), "case_id": case.id} for case in active_cases)
    activity.sort(key=lambda item: item["date"], reverse=True)

    return {
        "total_clients": clients or 0, "active_cases": cases or 0, "hearings_this_week": hearings or 0,
        "critical_action_items": critical or 0, "pending_drafts": drafts or 0, "pending_document_processing": docs or 0,
        "documents_ready": ready_docs or 0, "completed_scenarios": scenarios or 0,
        "focus_items": [{"id": item.id, "title": item.title, "description": item.next_step or item.description, "priority": item.priority, "due_date": _date(item.due_date), "case_id": item.case_id, "case_name": case_names.get(item.case_id)} for item in focus_items],
        "upcoming_events": [{"id": event.id, "title": event.title, "event_type": event.event_type, "event_date": _date(event.event_date), "severity": event.severity, "case_id": event.case_id, "case_name": case_names.get(event.case_id)} for event in upcoming_events],
        "matter_snapshot": [{"id": case.id, "case_name": case.case_name, "client_name": case_clients.get(case.client_id, "Client"), "matter_type": case.matter_type, "stage": case.current_stage, "risk_level": case.risk_level, "next_hearing_date": _date(case.next_hearing_date), "limitation_date": _date(case.limitation_date), "document_count": case_document_counts.get(case.id, 0)} for case in active_cases],
        "recent_activity": activity[:5],
    }
