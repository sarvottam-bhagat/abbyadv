from datetime import date
from pydantic import BaseModel
class ActionItemIn(BaseModel):
    title: str; description: str | None = None; next_step: str | None = None; client_id: str | None = None; case_id: str | None = None; priority: str = "medium"; due_date: date | None = None; status: str = "active"

