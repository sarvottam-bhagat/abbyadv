from pydantic import BaseModel

class DraftIn(BaseModel):
    client_id: str | None = None; case_id: str | None = None; scenario_id: str | None = None; draft_type: str; title: str; content: str | None = None


class DraftGenerateIn(BaseModel):
    title: str | None = None
    draft_type: str = "Legal notice"
    facts: str
    client_id: str | None = None
    case_id: str | None = None
    tone: str = "formal and professional"
    language: str = "English"


class DraftReviewIn(BaseModel):
    title: str | None = None
    content: str
    instruction: str = "Review this draft for clarity, professional tone, structure, and missing factual placeholders. Return a complete revised draft."
    client_id: str | None = None
    case_id: str | None = None


class DraftUploadStartIn(BaseModel):
    file_name: str
    mime_type: str | None = None
    client_id: str | None = None
    case_id: str | None = None


class DraftUploadCompleteIn(BaseModel):
    document_id: str
    title: str | None = None
    draft_type: str = "Legal draft"
    instruction: str = "Create a polished, editable legal draft based only on this uploaded document. Preserve the supplied facts and use placeholders where information is missing."
