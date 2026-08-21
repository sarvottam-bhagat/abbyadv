from pydantic import BaseModel
from src.api.schemas.common import ORM
class UserUpdate(BaseModel):
    full_name: str | None = None; firm_name: str | None = None; phone: str | None = None; default_state: str | None = None
class UserIn(UserUpdate): pass
class UserOut(ORM):
    id: str; auth_user_id: str; email: str | None; full_name: str; firm_name: str | None; phone: str | None; default_state: str | None; country: str

