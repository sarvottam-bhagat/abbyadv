from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
from src.api.schemas.common import ORM
class ClientIn(BaseModel):
    full_name: str = Field(min_length=1); email: str | None = None; phone: str | None = None; alternate_phone: str | None = None; client_type: str = "individual"; organization_name: str | None = None; address: str | None = None; city: str | None = None; state: str | None = None; postal_code: str | None = None; country: str = Field(default="IN", min_length=2, max_length=2); date_of_birth: date | None = None; occupation: str | None = None; id_type: str | None = None; id_number: str | None = None; preferred_contact_method: str | None = None; referred_by: str | None = None; notes: str | None = None; risk_level: str = "normal"; tags: list[str] | None = None

    @field_validator("country", mode="before")
    @classmethod
    def normalize_country(cls, value: str | None) -> str:
        normalized = str(value or "IN").strip().upper()
        aliases = {"INDIA": "IN", "BHARAT": "IN", "UNITED STATES": "US", "USA": "US", "UNITED KINGDOM": "GB"}
        return aliases.get(normalized, normalized)
class ClientOut(ORM):
    id: str; full_name: str; email: str | None; phone: str | None; alternate_phone: str | None; client_type: str; organization_name: str | None; address: str | None; city: str | None; state: str | None; postal_code: str | None; country: str; date_of_birth: date | None; occupation: str | None; id_type: str | None; id_number: str | None; preferred_contact_method: str | None; referred_by: str | None; status: str; risk_level: str; notes: str | None; tags: list | None; created_at: datetime
