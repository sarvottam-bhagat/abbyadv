from pydantic import BaseModel
class CaseWorkspaceResult(BaseModel):
    status: str
    case: dict

