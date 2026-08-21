from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.drafting import DraftAgent
from src.api.common import get_owned, save
from src.api.deps import get_current_user
from src.api.schemas.draft import DraftGenerateIn, DraftIn, DraftReviewIn, DraftUploadCompleteIn, DraftUploadStartIn
from src.api.schemas.draft_operation import DraftOperationIn
from src.database.base import get_db
from src.database.models import Case, CaseDocument, Client, Draft, User
from src.services.direct_document_ingestion import read_chat_attachment
from src.services.storage import StorageService
from src.services.draft_exports import build_docx, build_pdf

router = APIRouter(prefix="/api/drafts", tags=["Drafts"])


async def _context(db: AsyncSession, user: User, client_id: str | None, case_id: str | None) -> tuple[str, str | None, str | None]:
    client = await get_owned(db, Client, client_id, user.id) if client_id else None
    case = await get_owned(db, Case, case_id, user.id) if case_id else None
    if case and client and case.client_id != client.id:
        raise HTTPException(400, "Client does not own case")
    owner = client or (await get_owned(db, Client, case.client_id, user.id) if case else None)
    lines = []
    if owner:
        lines.append(f"Client: {owner.full_name}; address: {owner.address or '[not supplied]'}")
    if case:
        lines.extend([f"Matter: {case.case_name} ({case.matter_type})", f"Client role: {case.client_role or '[not supplied]'}", f"Opposite party: {case.opposite_party_name or '[not supplied]'}", f"Jurisdiction: {case.jurisdiction or case.state or '[not supplied]'}", f"Matter facts: {case.facts_summary or '[not supplied]'}", f"Relief sought: {case.relief_sought or '[not supplied]'}"])
    return "\n".join(lines), owner.id if owner else None, case.id if case else None


async def _save_generated(db: AsyncSession, user: User, content: str, title: str, draft_type: str, source_prompt: str, context: str, client_id: str | None, case_id: str | None) -> Draft:
    return await save(db, Draft(user_id=user.id, client_id=client_id, case_id=case_id, draft_type=draft_type, title=title, content=content, content_md=content, source_prompt=source_prompt, input_context={"matter_context": context}, status="draft"))


@router.post("", status_code=201)
async def create(payload: DraftIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    context, client_id, case_id = await _context(db, user, payload.client_id, payload.case_id)
    values = payload.model_dump(); values.update({"client_id": client_id, "case_id": case_id})
    return await save(db, Draft(user_id=user.id, **values))


@router.post("/generate", status_code=201)
async def generate(payload: DraftGenerateIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    context, client_id, case_id = await _context(db, user, payload.client_id, payload.case_id)
    instruction = f"Draft in {payload.language} with a {payload.tone} tone.\n\n{payload.facts}"
    content = await DraftAgent().generate(payload.draft_type, instruction, context)
    title = payload.title or payload.draft_type
    return await _save_generated(db, user, content, title, payload.draft_type, payload.facts, context, client_id, case_id)


@router.post("/review", status_code=201)
async def review(payload: DraftReviewIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    context, client_id, case_id = await _context(db, user, payload.client_id, payload.case_id)
    content = await DraftAgent().generate("Reviewed legal draft", f"{payload.instruction}\n\nSOURCE DRAFT:\n{payload.content}", context)
    return await _save_generated(db, user, content, payload.title or "Reviewed draft", "Reviewed legal draft", payload.instruction, context, client_id, case_id)


@router.post("/upload-url", status_code=201)
async def upload_url(payload: DraftUploadStartIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _, client_id, case_id = await _context(db, user, payload.client_id, payload.case_id)
    key = StorageService().key(user.auth_user_id, case_id or "draft-uploads", payload.file_name)
    document = CaseDocument(user_id=user.id, client_id=client_id, case_id=case_id, file_name=payload.file_name, file_type=payload.file_name.rsplit(".", 1)[-1] if "." in payload.file_name else None, mime_type=payload.mime_type, document_type="draft_attachment", storage_key=key, metadata_json={"source": "draft_upload", "persistent_knowledge": False})
    await save(db, document)
    return {"document_id": document.id, "storage_key": key, "upload_url": await StorageService().upload_url(key)}


@router.post("/upload-complete", status_code=201)
async def upload_complete(payload: DraftUploadCompleteIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    document = await get_owned(db, CaseDocument, payload.document_id, user.id)
    try:
        extracted = await read_chat_attachment(db, document)
    except (ValueError, RuntimeError) as exc:
        document.processing_status = "failed"; document.error_message = str(exc); await db.commit()
        raise HTTPException(422, str(exc))
    context, client_id, case_id = await _context(db, user, document.client_id, document.case_id)
    content = await DraftAgent().generate(payload.draft_type, f"{payload.instruction}\n\nUPLOADED DOCUMENT:\n{extracted}", context)
    return await _save_generated(db, user, content, payload.title or document.file_name.rsplit(".", 1)[0], payload.draft_type, payload.instruction, context, client_id, case_id)


@router.get("")
async def list_all(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return list((await db.execute(select(Draft).where(Draft.user_id == user.id).order_by(Draft.created_at.desc()))).scalars())


@router.get("/{draft_id}")
async def get(draft_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_owned(db, Draft, draft_id, user.id)


@router.get("/{draft_id}/export")
async def export(draft_id: str, format: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await get_owned(db, Draft, draft_id, user.id)
    content = item.content or item.content_md or ""
    safe_title = "".join(char if char.isalnum() or char in {"-", "_", " "} else "" for char in item.title).strip() or "abbyadv-draft"
    if format == "docx":
        return Response(build_docx(item.title, content), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={"Content-Disposition": f'attachment; filename="{safe_title}.docx"'})
    if format == "pdf":
        return Response(build_pdf(item.title, content), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{safe_title}.pdf"'})
    if format == "md":
        return Response(content, media_type="text/markdown", headers={"Content-Disposition": f'attachment; filename="{safe_title}.md"'})
    raise HTTPException(400, "Format must be md, docx, or pdf")


@router.patch("/{draft_id}")
async def update(draft_id: str, payload: DraftIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await get_owned(db, Draft, draft_id, user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    return await save(db, item)


@router.post("/{draft_id}/improve")
async def improve(draft_id: str, payload: DraftOperationIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await get_owned(db, Draft, draft_id, user.id)
    item.content = await DraftAgent().generate(item.draft_type, payload.instruction, item.content or "")
    item.content_md = item.content; item.version += 1
    return await save(db, item)
