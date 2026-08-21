from datetime import date
from pydantic import BaseModel
from src.api.schemas.common import ORM
class CaseIn(BaseModel):
    case_name: str; matter_type: str; country: str = "IN"; state: str | None = None; court_name: str | None = None; court_type: str | None = None; jurisdiction: str | None = None; case_number: str | None = None; cnr_number: str | None = None; fir_number: str | None = None; client_role: str | None = None; opposite_party_name: str | None = None; current_stage: str | None = None; next_hearing_date: date | None = None; limitation_date: date | None = None; relief_sought: str | None = None; facts_summary: str | None = None; risk_level: str = "normal"; tags: list[str] | None = None
class CaseOut(ORM):
    id: str; client_id: str; case_name: str; matter_type: str; country: str; state: str | None; court_name: str | None; court_type: str | None; jurisdiction: str | None; case_number: str | None; cnr_number: str | None; fir_number: str | None; client_role: str | None; opposite_party_name: str | None; current_stage: str | None; next_hearing_date: date | None; limitation_date: date | None; relief_sought: str | None; facts_summary: str | None; case_status: str; risk_level: str; tags: list | None

