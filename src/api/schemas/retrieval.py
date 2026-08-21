from pydantic import BaseModel, Field
class RetrievalIn(BaseModel):
    query: str = Field(min_length=1); case_id: str | None = None; document_id: str | None = None; limit: int = Field(default=10, ge=1, le=50)

