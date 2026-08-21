from typing import Literal
from pydantic import BaseModel
class ChatIn(BaseModel):
    question: str; session_id: str | None = None; client_ids: list[str] = []; case_ids: list[str] = []; document_ids: list[str] = []; mode: Literal["chat", "research"] = "chat"
class ChatAck(BaseModel):
    session_id: str; message_id: str; status: str; message: str

class ChatAttachmentUploadIn(BaseModel):
    file_name: str; mime_type: str | None = None; case_id: str | None = None; client_id: str | None = None; session_id: str | None = None; document_type: str | None = None

class ChatAttachmentCompleteIn(BaseModel):
    document_id: str; question: str; session_id: str | None = None; mode: Literal["chat", "research"] = "chat"
