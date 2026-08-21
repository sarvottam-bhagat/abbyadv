from pydantic import BaseModel
class ResearchIn(BaseModel):
    query: str; client_id: str | None = None; case_id: str | None = None

