from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.common import get_owned, save
from src.api.deps import get_current_user
from src.api.schemas.scenario import ScenarioIn
from src.agents.legal_engine import run_document_grounded_scenario, run_scenario, scenario_types
from src.database.base import get_db
from src.database.models import Case, CaseDocument, Client, LegalScenario, User
router = APIRouter(prefix="/api/scenarios", tags=["Scenarios"])
legacy_router = APIRouter(prefix="/api", tags=["Scenarios"])
@router.get("/types")
async def types(user: User = Depends(get_current_user)): return {"types": scenario_types()}
@router.post("", status_code=201)
async def create(payload: ScenarioIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await get_owned(db, Client, payload.client_id, user.id); case = await get_owned(db, Case, payload.case_id, user.id)
    if case.client_id != payload.client_id: raise HTTPException(400, "Case does not belong to client")
    documents: list[CaseDocument] = []
    if payload.document_ids:
        documents = list((await db.execute(select(CaseDocument).where(CaseDocument.id.in_(payload.document_ids), CaseDocument.user_id == user.id))).scalars())
        if len(documents) != len(set(payload.document_ids)) or any(item.case_id != case.id for item in documents):
            raise HTTPException(400, "Scenario documents must belong to the selected case")
        pending = [item.file_name for item in documents if item.processing_status != "processed" or not item.extracted_text]
        if pending:
            raise HTTPException(409, "Wait for ABBYY extraction to finish: " + ", ".join(pending))
    values = payload.model_dump(); values["uploaded_document_ids"] = values.pop("document_ids")
    scenario = LegalScenario(user_id=user.id, **values, status="processing", execution_status="processing")
    await save(db, scenario)
    case_context = {
        "case_name": case.case_name, "matter_type": case.matter_type, "state": case.state,
        "jurisdiction": case.jurisdiction, "court_name": case.court_name, "case_number": case.case_number,
        "client_role": case.client_role, "opposite_party_name": case.opposite_party_name,
        "current_stage": case.current_stage, "facts_summary": case.facts_summary, "relief_sought": case.relief_sought,
        "next_hearing_date": case.next_hearing_date, "limitation_date": case.limitation_date,
    }
    evidence = [{"file_name": item.file_name, "text": item.extracted_text or ""} for item in documents]
    try:
        supported = {item["event_type"] for item in scenario_types()}
        scenario.result = await run_document_grounded_scenario(payload.event_type, payload.input_parameters, case_context, evidence) if payload.event_type in supported else run_scenario(payload.event_type, payload.input_parameters)
        scenario.status = "success"; scenario.execution_status = "success"
        scenario.tool_trace = [{"tool": "abbyy_direct_document_context", "status": "success", "document_count": len(evidence)}, {"tool": "practice_area_scenario_agent", "status": "success", "event_type": payload.event_type}]
        scenario.citations = [{"document_id": item.id, "file_name": item.file_name} for item in documents]
        await db.commit(); await db.refresh(scenario)
        return scenario
    except Exception as exc:
        scenario.status = "failed"; scenario.execution_status = "failed"; scenario.error_message = str(exc)
        await db.commit()
        raise HTTPException(502, "Scenario analysis could not be generated. Please try again.") from exc
@router.get("/{scenario_id}")
async def get(scenario_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)): return await get_owned(db, LegalScenario, scenario_id, user.id)
@router.get("/case/{case_id}")
async def list_for_case(case_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await get_owned(db, Case, case_id, user.id); return list((await db.execute(select(LegalScenario).where(LegalScenario.case_id == case_id, LegalScenario.user_id == user.id))).scalars())

@legacy_router.get("/cases/{case_id}/scenarios")
async def list_for_case_legacy(case_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await get_owned(db, Case, case_id, user.id); return list((await db.execute(select(LegalScenario).where(LegalScenario.case_id == case_id, LegalScenario.user_id == user.id))).scalars())
