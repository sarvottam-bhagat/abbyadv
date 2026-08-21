from fastapi import APIRouter, Depends, HTTPException, Query
import json
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.common import get_owned, save
from src.api.deps import get_current_user
from src.api.schemas.document import DocumentIn, DocumentOut, KnowledgeDocumentOut
from src.database.base import get_db
from src.database.models import Case, CaseDocument, Client, User
from src.services.storage import StorageService
from src.services.abbyy import AbbyyError, AbbyyVantageClient, extract_ocr_text
from src.services.document_pipeline import index_document
from src.services.direct_document_ingestion import ingest_chat_attachment
from src.core.config import get_settings
router = APIRouter(prefix="/api", tags=["Documents"])
ABBYY_OCR_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}


async def _start_abbyy_processing(item: CaseDocument, db: AsyncSession) -> CaseDocument:
    """Queue a scanned or otherwise non-extractable document with ABBYY."""
    settings = get_settings()
    if not settings.abbyy_client_id or not settings.abbyy_client_secret or not settings.abbyy_skill_id:
        raise HTTPException(503, "ABBYY is not configured. Set ABBYY_CLIENT_ID, ABBYY_CLIENT_SECRET, and ABBYY_SKILL_ID.")
    client = AbbyyVantageClient()
    try:
        content = await StorageService().download(item.storage_key)
        token = await client.get_token()
        if len(content) < 30 * 1024 * 1024:
            transaction_id = await client.launch(token, content, item.file_name, item.mime_type, settings.abbyy_skill_id)
        else:
            transaction_id = await client.launch_separate(token, content, item.file_name, item.mime_type, settings.abbyy_skill_id)
        item.abbyy_transaction_id = transaction_id
        item.processing_status = "processing"
        item.ocr_status = "processing"
        item.error_message = None
        await db.commit()
        await db.refresh(item)
        return item
    except (AbbyyError, RuntimeError) as exc:
        item.processing_status = "failed"
        item.ocr_status = "failed"
        item.error_message = str(exc)
        await db.commit()
        raise HTTPException(502, str(exc))
    finally:
        await client.close()
@router.post("/documents/upload-url", status_code=201)
async def create_upload(payload: DocumentIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    case = await get_owned(db, Case, payload.case_id, user.id)
    if payload.client_id and payload.client_id != case.client_id: raise HTTPException(400, "Client does not own case")
    key = StorageService().key(user.auth_user_id, case.id, payload.file_name)
    values = payload.model_dump(); values["client_id"] = case.client_id
    item = CaseDocument(user_id=user.id, storage_key=key, **values); await save(db, item)
    return {"document_id": item.id, "upload_url": await StorageService().upload_url(key), "storage_key": key, "status": item.processing_status}
@router.get("/cases/{case_id}/documents", response_model=list[DocumentOut])
async def list_for_case(case_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await get_owned(db, Case, case_id, user.id); return list((await db.execute(select(CaseDocument).where(CaseDocument.case_id == case_id, CaseDocument.user_id == user.id))).scalars())


@router.get("/knowledge-base/documents", response_model=list[KnowledgeDocumentOut])
async def list_knowledge_base(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Return only the current advocate's documents, with their client and matter labels."""
    rows = (await db.execute(
        select(CaseDocument, Client.full_name, Case.case_name)
        .join(Client, CaseDocument.client_id == Client.id)
        .join(Case, CaseDocument.case_id == Case.id)
        .where(CaseDocument.user_id == user.id, or_(CaseDocument.document_type.is_(None), CaseDocument.document_type != "chat_attachment"))
        .order_by(CaseDocument.created_at.desc())
    )).all()
    return [
        {**DocumentOut.model_validate(document).model_dump(), "client_name": client_name, "case_name": case_name, "created_at": document.created_at}
        for document, client_name, case_name in rows
    ]
@router.get("/documents/{document_id}", response_model=DocumentOut)
async def get(document_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)): return await get_owned(db, CaseDocument, document_id, user.id)
@router.post("/documents/{document_id}/process", response_model=DocumentOut)
async def process(
    document_id: str,
    use_abbyy: bool = Query(False),
    direct_context_only: bool = Query(False),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await get_owned(db, CaseDocument, document_id, user.id)
    if (item.embedding_status == "processed" or item.processing_status == "processed") and item.extracted_text:
        return item
    if use_abbyy:
        # Scenario evidence is intentionally ABBYY-first. Its extracted text is
        # supplied directly to the scenario agent, rather than indexed in Qdrant.
        item.metadata_json = {**(item.metadata_json or {}), "direct_context_only": direct_context_only}
        await db.commit()
        return await _start_abbyy_processing(item, db)
    try:
        # Most uploaded files can be parsed and indexed immediately. This makes them
        # available to case-aware chat without waiting for OCR.
        await ingest_chat_attachment(db, item)
        await db.refresh(item)
        return item
    except ValueError as exc:
        if any(item.file_name.lower().endswith(extension) for extension in ABBYY_OCR_EXTENSIONS):
            return await _start_abbyy_processing(item, db)
        item.processing_status = "failed"
        item.error_message = str(exc)
        await db.commit()
        raise HTTPException(422, str(exc))
    except RuntimeError as exc:
        item.processing_status = "failed"
        item.error_message = str(exc)
        await db.commit()
        raise HTTPException(502, str(exc))

@router.get("/documents/{document_id}/processing-status", response_model=DocumentOut)
@router.post("/documents/{document_id}/processing-status", response_model=DocumentOut)
async def processing_status(document_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await get_owned(db, CaseDocument, document_id, user.id)
    if not item.abbyy_transaction_id: return item
    settings = get_settings(); client = AbbyyVantageClient()
    try:
        token = await client.get_token(); result = await client.transaction(token, item.abbyy_transaction_id); status = result.get("status") or result.get("state")
        if status in {"Processed", "ProcessedWithWarnings"}:
            files = await client.download_result_files(token, item.abbyy_transaction_id, result); text_parts=[]
            for file_info in files:
                raw=file_info["content"]
                try:
                    parsed=json.loads(raw.decode("utf-8")); text_parts.append(extract_ocr_text(parsed) if isinstance(parsed, dict) else str(parsed))
                except (UnicodeDecodeError, json.JSONDecodeError): text_parts.append(raw.decode("utf-8", errors="ignore"))
            extracted_text = "\n\n".join(part for part in text_parts if part).strip()
            if not extracted_text:
                raise AbbyyError("ABBYY completed but did not return readable OCR text")
            item.extracted_text=extracted_text; item.processing_status="processed"; item.ocr_status="processed"; await db.commit()
            if not (item.metadata_json or {}).get("direct_context_only"):
                await index_document(db, item)
        elif status in {"NotProcessed", "Deleted"}: item.processing_status="failed"; item.ocr_status="failed"; item.error_message=f"ABBYY transaction ended with status {status}"; await db.commit()
        else: item.processing_status="processing"; await db.commit()
        await db.refresh(item); return item
    except AbbyyError as exc:
        item.processing_status="failed"; item.ocr_status="failed"; item.error_message=str(exc); await db.commit(); raise HTTPException(502, str(exc))
    finally: await client.close()
