from datetime import datetime
from pydantic import BaseModel
from src.api.schemas.common import ORM
class DocumentIn(BaseModel):
    client_id: str | None = None; case_id: str; file_name: str; mime_type: str | None = None; document_type: str | None = None
class DocumentOut(ORM):
    id: str; client_id: str | None; case_id: str; file_name: str; mime_type: str | None; document_type: str | None; storage_key: str; processing_status: str; ocr_status: str; embedding_status: str; abbyy_transaction_id: str | None; extracted_text: str | None; error_message: str | None

class KnowledgeDocumentOut(DocumentOut):
    client_name: str
    case_name: str
    created_at: datetime
