from pydantic import BaseModel
class PartyIn(BaseModel):
    name: str; party_type: str; role: str | None = None; contact_json: dict | None = None; address_json: dict | None = None; notes: str | None = None

