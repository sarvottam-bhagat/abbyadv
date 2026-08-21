from datetime import date
from pydantic import BaseModel
class EventIn(BaseModel):
    title: str; event_type: str = "task"; event_date: date; client_id: str | None = None; case_id: str | None = None; severity: str = "normal"; notes: str | None = None

