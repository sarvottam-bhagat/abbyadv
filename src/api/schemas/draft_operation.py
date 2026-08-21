from pydantic import BaseModel
class DraftOperationIn(BaseModel):
    instruction: str
