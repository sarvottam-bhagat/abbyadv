from pydantic import BaseModel
class ScenarioIn(BaseModel):
    client_id: str; case_id: str; name: str; event_type: str; input_parameters: dict = {}; document_ids: list[str] = []

