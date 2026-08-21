from pydantic import BaseModel
class ReportIn(BaseModel):
    report_type: str = "case_summary"; client_id: str | None = None; case_id: str | None = None; format: str = "pdf"

