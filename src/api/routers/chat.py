from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
import json
from storage3.exceptions import StorageApiError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.common import get_owned, save
from src.api.deps import get_current_user
from src.api.schemas.chat import ChatAck, ChatAttachmentCompleteIn, ChatAttachmentUploadIn, ChatIn
from src.database.base import get_db
from src.database.models import Case, CaseDocument, ChatMessage, ChatSession, Client, User
from src.agents.chat.chat_agent import ChatAgent, ChatContext
from src.agents.research import ResearchAgent
from src.services.direct_document_ingestion import read_chat_attachment
from src.services.storage import StorageService
router = APIRouter(prefix="/api/chat", tags=["Chat"])


def agent_for(mode: str):
    return ResearchAgent() if mode == "research" else ChatAgent()


@router.get("/bootstrap")
async def chat_bootstrap(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Load the selectors and saved chats together for a fast chat startup."""
    clients = list((await db.execute(select(Client).where(Client.user_id == user.id).order_by(Client.full_name))).scalars())
    sessions = list((await db.execute(select(ChatSession).where(ChatSession.user_id == user.id).order_by(ChatSession.created_at.desc()))).scalars())
    return {"clients": clients, "sessions": sessions}


async def case_snapshot(db: AsyncSession, user_id: str, case_ids: list[str]) -> list[dict]:
    """Compact structured matter context that complements retrieved document chunks."""
    if not case_ids:
        return []
    rows = (await db.execute(
        select(Case, Client.full_name)
        .join(Client, Case.client_id == Client.id)
        .where(Case.user_id == user_id, Case.id.in_(case_ids))
    )).all()
    if len(rows) != len(set(case_ids)):
        raise HTTPException(404, "One or more selected cases were not found")
    return [{
        "case_id": matter.id, "case_name": matter.case_name, "matter_type": matter.matter_type,
        "client_name": client_name, "client_role": matter.client_role, "opposite_party": matter.opposite_party_name,
        "stage": matter.current_stage, "jurisdiction": matter.jurisdiction or matter.state,
        "court_name": matter.court_name, "reference": matter.case_number or matter.cnr_number or matter.fir_number,
        "facts_summary": matter.facts_summary, "relief_sought": matter.relief_sought,
        "next_hearing_date": matter.next_hearing_date, "limitation_date": matter.limitation_date,
    } for matter, client_name in rows]


@router.post("/attachments/upload-url", status_code=201)
async def attachment_upload_url(payload: ChatAttachmentUploadIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    case = await get_owned(db, Case, payload.case_id, user.id) if payload.case_id else None
    client_id = case.client_id if case else payload.client_id
    if client_id:
        await get_owned(db, Client, client_id, user.id)
    if case and payload.client_id and payload.client_id != case.client_id:
        raise HTTPException(400, "Client does not own case")
    session = await get_owned(db, ChatSession, payload.session_id, user.id) if payload.session_id else await save(db, ChatSession(user_id=user.id, title=payload.file_name[:80], client_ids=[client_id] if client_id else [], case_ids=[case.id] if case else []))
    key = StorageService().key(user.auth_user_id, case.id if case else f"chat/{session.id}", payload.file_name)
    document = CaseDocument(user_id=user.id, client_id=client_id, case_id=case.id if case else None, file_name=payload.file_name, file_type=payload.file_name.rsplit(".", 1)[-1] if "." in payload.file_name else None, mime_type=payload.mime_type, document_type="chat_attachment", storage_key=key, metadata_json={"source": "chat_attachment", "persistent_knowledge": False})
    await save(db, document)
    return {"document_id": document.id, "session_id": session.id, "storage_key": key, "upload_url": await StorageService().upload_url(key), "status": "uploaded"}


@router.post("/attachments/complete", response_model=ChatAck, status_code=201)
async def attachment_complete(payload: ChatAttachmentCompleteIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    document = await get_owned(db, CaseDocument, payload.document_id, user.id)
    session = await get_owned(db, ChatSession, payload.session_id, user.id) if payload.session_id else await save(db, ChatSession(user_id=user.id, title=payload.question[:80], client_ids=[document.client_id], case_ids=[document.case_id]))
    try:
        direct_text = await read_chat_attachment(db, document)
        snapshot = await case_snapshot(db, user.id, [document.case_id] if document.case_id else [])
        result = await agent_for(payload.mode).answer(payload.question, ChatContext([document.client_id] if document.client_id else [], [document.case_id] if document.case_id else [], [], snapshot, direct_text), user.id)
    except (ValueError, RuntimeError, StorageApiError) as exc:
        document.processing_status = "failed"; document.error_message = str(exc); await db.commit()
        raise HTTPException(422, str(exc))
    user_message = ChatMessage(session_id=session.id, role="user", content=payload.question, status="success", metadata_json={"document_ids": [document.id]})
    assistant = ChatMessage(session_id=session.id, role="assistant", content=result["answer"], status="success", metadata_json=jsonable_encoder({"citations": result["citations"], "confidence": result["confidence"], "context": result["context"]}), tool_trace=jsonable_encoder(result["tool_trace"]), citations=jsonable_encoder(result["citations"]))
    db.add_all([user_message, assistant]); await db.commit()
    return ChatAck(session_id=session.id, message_id=assistant.id, status="success", message=assistant.content)


@router.post("/attachments/complete/stream")
async def attachment_complete_stream(payload: ChatAttachmentCompleteIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Answer a one-off attachment over SSE without indexing it in Qdrant."""
    document = await get_owned(db, CaseDocument, payload.document_id, user.id)
    session = await get_owned(db, ChatSession, payload.session_id, user.id) if payload.session_id else await save(db, ChatSession(user_id=user.id, title=payload.question[:80], client_ids=[document.client_id] if document.client_id else [], case_ids=[document.case_id] if document.case_id else []))
    try:
        direct_text = await read_chat_attachment(db, document)
        snapshot = await case_snapshot(db, user.id, [document.case_id] if document.case_id else [])
    except (ValueError, RuntimeError, StorageApiError) as exc:
        document.processing_status = "failed"; document.error_message = str(exc); await db.commit()
        raise HTTPException(422, str(exc))

    user_message = ChatMessage(session_id=session.id, role="user", content=payload.question, status="success", metadata_json={"document_ids": [document.id]})
    assistant = ChatMessage(session_id=session.id, role="assistant", content="", status="streaming")
    db.add_all([user_message, assistant]); await db.commit(); await db.refresh(assistant)

    async def events():
        yield f"event: start\ndata: {json.dumps({'session_id': session.id, 'message_id': assistant.id})}\n\n"
        try:
            context = ChatContext([document.client_id] if document.client_id else [], [document.case_id] if document.case_id else [], [], snapshot, direct_text)
            async for event in agent_for(payload.mode).stream_answer(payload.question, context, user.id):
                if event["type"] == "token":
                    yield f"event: token\ndata: {json.dumps({'token': event['token']})}\n\n"
                    continue
                result = event["result"]
                assistant.content = result["answer"]; assistant.status = "success"; assistant.metadata_json = jsonable_encoder({"citations": result["citations"], "confidence": result["confidence"], "context": result["context"]}); assistant.tool_trace = jsonable_encoder(result["tool_trace"]); assistant.citations = jsonable_encoder(result["citations"])
                await db.commit()
                yield f"event: done\ndata: {json.dumps({'session_id': session.id, 'message_id': assistant.id, 'citations': result['citations']})}\n\n"
        except Exception as exc:
            assistant.status = "failed"; assistant.error_message = str(exc); await db.commit()
            yield f"event: error\ndata: {json.dumps({'detail': 'Unable to generate an answer right now.'})}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@router.post("", response_model=ChatAck, status_code=201)
async def create_message(payload: ChatIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    snapshot = await case_snapshot(db, user.id, payload.case_ids)
    if payload.session_id: session = await get_owned(db, ChatSession, payload.session_id, user.id)
    else: session = await save(db, ChatSession(user_id=user.id, title=payload.question[:80], client_ids=payload.client_ids, case_ids=payload.case_ids))
    user_message = ChatMessage(session_id=session.id, role="user", content=payload.question, status="success", metadata_json=payload.model_dump(mode="json")); db.add(user_message); await db.flush()
    result = await agent_for(payload.mode).answer(payload.question, ChatContext(payload.client_ids, payload.case_ids, payload.document_ids, snapshot), user.id)
    assistant = ChatMessage(session_id=session.id, role="assistant", content=result["answer"], status="success", metadata_json=jsonable_encoder({"citations": result["citations"], "confidence": result["confidence"], "context": result["context"]}), tool_trace=jsonable_encoder(result["tool_trace"]), citations=jsonable_encoder(result["citations"])); db.add(assistant); await db.commit()
    return ChatAck(session_id=session.id, message_id=assistant.id, status="success", message=assistant.content)

@router.post("/stream")
async def create_message_stream(payload: ChatIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    snapshot = await case_snapshot(db, user.id, payload.case_ids)
    session = await get_owned(db, ChatSession, payload.session_id, user.id) if payload.session_id else await save(db, ChatSession(user_id=user.id, title=payload.question[:80], client_ids=payload.client_ids, case_ids=payload.case_ids))
    user_message = ChatMessage(session_id=session.id, role="user", content=payload.question, status="success", metadata_json=payload.model_dump(mode="json"))
    assistant = ChatMessage(session_id=session.id, role="assistant", content="", status="streaming")
    db.add_all([user_message, assistant]); await db.commit(); await db.refresh(assistant)

    async def events():
        yield f"event: start\ndata: {json.dumps({'session_id': session.id, 'message_id': assistant.id})}\n\n"
        try:
            async for event in agent_for(payload.mode).stream_answer(payload.question, ChatContext(payload.client_ids, payload.case_ids, payload.document_ids, snapshot), user.id):
                if event["type"] == "token":
                    yield f"event: token\ndata: {json.dumps({'token': event['token']})}\n\n"
                    continue
                result = event["result"]
                assistant.content = result["answer"]; assistant.status = "success"; assistant.metadata_json = jsonable_encoder({"citations": result["citations"], "confidence": result["confidence"], "context": result["context"]}); assistant.tool_trace = jsonable_encoder(result["tool_trace"]); assistant.citations = jsonable_encoder(result["citations"])
                await db.commit()
                yield f"event: done\ndata: {json.dumps({'session_id': session.id, 'message_id': assistant.id, 'citations': result['citations']})}\n\n"
        except Exception as exc:
            assistant.status = "failed"; assistant.error_message = str(exc); await db.commit()
            yield f"event: error\ndata: {json.dumps({'detail': 'Unable to generate an answer right now.'})}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control":"no-cache", "X-Accel-Buffering":"no"})
@router.get("/sessions")
async def list_sessions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)): return list((await db.execute(select(ChatSession).where(ChatSession.user_id == user.id).order_by(ChatSession.created_at.desc()))).scalars())
@router.get("/sessions/{session_id}")
async def get_session(session_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    session = await get_owned(db, ChatSession, session_id, user.id); await db.refresh(session, ["messages"]); return {"id": session.id, "title": session.title, "messages": [{"id": m.id, "role": m.role, "content": m.content, "status": m.status, "citations": m.citations or []} for m in session.messages]}

@router.get("/stream/{message_id}")
async def stream_message(message_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    message = (await db.execute(select(ChatMessage).join(ChatSession).where(ChatMessage.id == message_id, ChatSession.user_id == user.id))).scalar_one_or_none()
    if message is None: raise HTTPException(404, "Message not found")
    async def events():
        yield f"event: status\ndata: {json.dumps({'status': message.status})}\n\n"
        yield f"event: answer\ndata: {json.dumps({'message_id': message.id, 'content': message.content})}\n\n"
        yield "event: done\ndata: {}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})
