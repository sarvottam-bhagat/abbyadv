from datetime import date, datetime
from uuid import uuid4
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, JSON, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base

def uid() -> str: return str(uuid4())

class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class User(Timestamped, Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    auth_user_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(320))
    full_name: Mapped[str] = mapped_column(String(200), default="Advocate")
    firm_name: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(50))
    default_state: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(2), default="IN")
    clients: Mapped[list["Client"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Client(Timestamped, Base):
    __tablename__ = "clients"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(320)); phone: Mapped[str | None] = mapped_column(String(50))
    client_type: Mapped[str] = mapped_column(String(40), default="individual")
    city: Mapped[str | None] = mapped_column(String(100)); state: Mapped[str | None] = mapped_column(String(100)); country: Mapped[str] = mapped_column(String(2), default="IN")
    status: Mapped[str] = mapped_column(String(30), default="active"); risk_level: Mapped[str] = mapped_column(String(30), default="normal")
    notes: Mapped[str | None] = mapped_column(Text); tags: Mapped[list | None] = mapped_column(JSON)
    alternate_phone: Mapped[str | None] = mapped_column(String(50)); address: Mapped[str | None] = mapped_column(Text); postal_code: Mapped[str | None] = mapped_column(String(20)); date_of_birth: Mapped[date | None] = mapped_column(Date); occupation: Mapped[str | None] = mapped_column(String(150)); id_type: Mapped[str | None] = mapped_column(String(50)); id_number: Mapped[str | None] = mapped_column(String(100)); preferred_contact_method: Mapped[str | None] = mapped_column(String(30)); organization_name: Mapped[str | None] = mapped_column(String(250)); referred_by: Mapped[str | None] = mapped_column(String(200))
    user: Mapped[User] = relationship(back_populates="clients"); cases: Mapped[list["Case"]] = relationship(back_populates="client", cascade="all, delete-orphan")

class Case(Timestamped, Base):
    __tablename__ = "cases"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True); client_id: Mapped[str] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    case_name: Mapped[str] = mapped_column(String(250)); matter_type: Mapped[str] = mapped_column(String(60)); country: Mapped[str] = mapped_column(String(2), default="IN")
    state: Mapped[str | None] = mapped_column(String(100)); court_name: Mapped[str | None] = mapped_column(String(200)); court_type: Mapped[str | None] = mapped_column(String(80)); jurisdiction: Mapped[str | None] = mapped_column(String(120))
    case_number: Mapped[str | None] = mapped_column(String(100)); cnr_number: Mapped[str | None] = mapped_column(String(100)); fir_number: Mapped[str | None] = mapped_column(String(100))
    client_role: Mapped[str | None] = mapped_column(String(80)); opposite_party_name: Mapped[str | None] = mapped_column(String(200)); current_stage: Mapped[str | None] = mapped_column(String(120))
    next_hearing_date: Mapped[date | None] = mapped_column(Date); limitation_date: Mapped[date | None] = mapped_column(Date); relief_sought: Mapped[str | None] = mapped_column(Text); facts_summary: Mapped[str | None] = mapped_column(Text)
    case_status: Mapped[str] = mapped_column(String(30), default="active"); risk_level: Mapped[str] = mapped_column(String(30), default="normal"); tags: Mapped[list | None] = mapped_column(JSON)
    client: Mapped[Client] = relationship(back_populates="cases")

class CaseDocument(Timestamped, Base):
    __tablename__ = "case_documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True); client_id: Mapped[str | None] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE")); case_id: Mapped[str | None] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    file_name: Mapped[str] = mapped_column(String(255)); file_type: Mapped[str | None] = mapped_column(String(80)); mime_type: Mapped[str | None] = mapped_column(String(120)); document_type: Mapped[str | None] = mapped_column(String(80)); storage_key: Mapped[str] = mapped_column(String(500)); storage_bucket: Mapped[str] = mapped_column(String(120), default="case-documents"); processing_status: Mapped[str] = mapped_column(String(30), default="uploaded"); ocr_status: Mapped[str] = mapped_column(String(30), default="not_started"); embedding_status: Mapped[str] = mapped_column(String(30), default="not_started"); abbyy_transaction_id: Mapped[str | None] = mapped_column(String(200), index=True); extracted_text: Mapped[str | None] = mapped_column(Text); summary: Mapped[str | None] = mapped_column(Text); extracted_facts: Mapped[dict | None] = mapped_column(JSON); ocr_metadata: Mapped[dict | None] = mapped_column(JSON); page_count: Mapped[int | None] = mapped_column(Integer); confidence_score: Mapped[float | None] = mapped_column(); error_message: Mapped[str | None] = mapped_column(Text); metadata_json: Mapped[dict | None] = mapped_column(JSON)

class ChatSession(Timestamped, Base):
    __tablename__ = "chat_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True); title: Mapped[str] = mapped_column(String(200), default="New chat"); mode: Mapped[str] = mapped_column(String(30), default="chat"); client_ids: Mapped[list | None] = mapped_column(JSON); case_ids: Mapped[list | None] = mapped_column(JSON); context_meta: Mapped[dict | None] = mapped_column(JSON)
    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Timestamped, Base):
    __tablename__ = "chat_messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True); role: Mapped[str] = mapped_column(String(20)); content: Mapped[str] = mapped_column(Text); status: Mapped[str] = mapped_column(String(30), default="success"); error_message: Mapped[str | None] = mapped_column(Text); metadata_json: Mapped[dict | None] = mapped_column(JSON); tool_trace: Mapped[list | None] = mapped_column(JSON); citations: Mapped[list | None] = mapped_column(JSON)
    session: Mapped[ChatSession] = relationship(back_populates="messages")

class LegalScenario(Timestamped, Base):
    __tablename__ = "legal_scenarios"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True); client_id: Mapped[str] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE")); case_id: Mapped[str | None] = mapped_column(ForeignKey("cases.id", ondelete="SET NULL"), index=True); name: Mapped[str] = mapped_column(String(250)); description: Mapped[str | None] = mapped_column(Text); country: Mapped[str] = mapped_column(String(2), default="IN"); state: Mapped[str | None] = mapped_column(String(100)); scenario_type: Mapped[str] = mapped_column(String(80), default="legal"); event_type: Mapped[str] = mapped_column(String(80)); input_parameters: Mapped[dict | None] = mapped_column(JSON); uploaded_document_ids: Mapped[list | None] = mapped_column(JSON); status: Mapped[str] = mapped_column(String(30), default="pending"); execution_status: Mapped[str] = mapped_column(String(30), default="pending"); error_message: Mapped[str | None] = mapped_column(Text); result: Mapped[dict | None] = mapped_column(JSON); tool_trace: Mapped[list | None] = mapped_column(JSON); citations: Mapped[list | None] = mapped_column(JSON); is_template: Mapped[bool] = mapped_column(Boolean, default=False)

class Draft(Timestamped, Base):
    __tablename__ = "drafts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True); client_id: Mapped[str | None] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL")); case_id: Mapped[str | None] = mapped_column(ForeignKey("cases.id", ondelete="SET NULL")); scenario_id: Mapped[str | None] = mapped_column(ForeignKey("legal_scenarios.id", ondelete="SET NULL")); draft_type: Mapped[str] = mapped_column(String(80)); title: Mapped[str] = mapped_column(String(250)); content: Mapped[str | None] = mapped_column(Text); content_md: Mapped[str | None] = mapped_column(Text); content_html: Mapped[str | None] = mapped_column(Text); source_prompt: Mapped[str | None] = mapped_column(Text); input_context: Mapped[dict | None] = mapped_column(JSON); citations: Mapped[list | None] = mapped_column(JSON); version: Mapped[int] = mapped_column(Integer, default=1); status: Mapped[str] = mapped_column(String(30), default="draft")

class ResearchMemo(Timestamped, Base):
    __tablename__ = "research_memos"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True); client_id: Mapped[str | None] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL")); case_id: Mapped[str | None] = mapped_column(ForeignKey("cases.id", ondelete="SET NULL")); title: Mapped[str] = mapped_column(String(250), default="Research memo"); query: Mapped[str] = mapped_column(Text); answer: Mapped[str | None] = mapped_column(Text); research_type: Mapped[str | None] = mapped_column(String(80)); sources: Mapped[list | None] = mapped_column(JSON); status: Mapped[str] = mapped_column(String(30), default="success"); citations: Mapped[list | None] = mapped_column(JSON); tool_trace: Mapped[list | None] = mapped_column(JSON)

class LegalEvent(Timestamped, Base):
    __tablename__ = "legal_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True); client_id: Mapped[str | None] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE")); case_id: Mapped[str | None] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE")); title: Mapped[str] = mapped_column(String(250)); event_type: Mapped[str] = mapped_column(String(50), default="task"); source: Mapped[str] = mapped_column(String(30), default="manual"); event_date: Mapped[date] = mapped_column(Date); start_date: Mapped[date | None] = mapped_column(Date); end_date: Mapped[date | None] = mapped_column(Date); severity: Mapped[str] = mapped_column(String(30), default="normal"); status: Mapped[str] = mapped_column(String(30), default="active"); is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False); reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True)); notes: Mapped[str | None] = mapped_column(Text); description: Mapped[str | None] = mapped_column(Text); metadata_json: Mapped[dict | None] = mapped_column(JSON)

class CaseParty(Timestamped, Base):
    __tablename__ = "case_parties"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); case_id: Mapped[str] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True); name: Mapped[str] = mapped_column(String(200)); party_type: Mapped[str] = mapped_column(String(50)); role: Mapped[str | None] = mapped_column(String(100)); contact_json: Mapped[dict | None] = mapped_column(JSON); address_json: Mapped[dict | None] = mapped_column(JSON); notes: Mapped[str | None] = mapped_column(Text)

class DocumentChunk(Timestamped, Base):
    __tablename__ = "document_chunks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); document_id: Mapped[str] = mapped_column(ForeignKey("case_documents.id", ondelete="CASCADE"), index=True); user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True); client_id: Mapped[str | None] = mapped_column(String(36)); case_id: Mapped[str | None] = mapped_column(String(36), index=True); chunk_index: Mapped[int] = mapped_column(Integer); content: Mapped[str] = mapped_column(Text); content_hash: Mapped[str | None] = mapped_column(String(128)); page_start: Mapped[int | None] = mapped_column(Integer); page_end: Mapped[int | None] = mapped_column(Integer); section_title: Mapped[str | None] = mapped_column(String(250)); metadata_json: Mapped[dict | None] = mapped_column(JSON); vector_id: Mapped[str | None] = mapped_column(String(200))

class LegalSource(Timestamped, Base):
    __tablename__ = "legal_sources"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); country: Mapped[str] = mapped_column(String(2)); state: Mapped[str | None] = mapped_column(String(100)); source_type: Mapped[str] = mapped_column(String(50)); title: Mapped[str] = mapped_column(String(300)); citation: Mapped[str | None] = mapped_column(String(300)); authority_level: Mapped[str | None] = mapped_column(String(50)); court: Mapped[str | None] = mapped_column(String(200)); year: Mapped[int | None] = mapped_column(Integer); practice_area: Mapped[str | None] = mapped_column(String(100)); source_url: Mapped[str | None] = mapped_column(String(500)); storage_key: Mapped[str | None] = mapped_column(String(500)); metadata_json: Mapped[dict | None] = mapped_column(JSON)

class LegalSourceChunk(Timestamped, Base):
    __tablename__ = "legal_source_chunks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); source_id: Mapped[str] = mapped_column(ForeignKey("legal_sources.id", ondelete="CASCADE"), index=True); country: Mapped[str] = mapped_column(String(2)); state: Mapped[str | None] = mapped_column(String(100)); source_type: Mapped[str] = mapped_column(String(50)); practice_area: Mapped[str | None] = mapped_column(String(100)); heading: Mapped[str | None] = mapped_column(String(250)); content: Mapped[str] = mapped_column(Text); citation: Mapped[str | None] = mapped_column(String(300)); paragraph_number: Mapped[str | None] = mapped_column(String(50)); section_number: Mapped[str | None] = mapped_column(String(50)); metadata_json: Mapped[dict | None] = mapped_column(JSON); vector_id: Mapped[str | None] = mapped_column(String(200))

class ActionItem(Timestamped, Base):
    __tablename__ = "action_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True); client_id: Mapped[str | None] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE")); case_id: Mapped[str | None] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE")); source_type: Mapped[str | None] = mapped_column(String(50)); source_id: Mapped[str | None] = mapped_column(String(36)); title: Mapped[str] = mapped_column(String(250)); description: Mapped[str | None] = mapped_column(Text); next_step: Mapped[str | None] = mapped_column(Text); priority: Mapped[str] = mapped_column(String(30), default="medium"); status: Mapped[str] = mapped_column(String(30), default="active"); due_date: Mapped[date | None] = mapped_column(Date); tags: Mapped[list | None] = mapped_column(JSON)

class ReportJob(Timestamped, Base):
    __tablename__ = "report_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True); client_id: Mapped[str | None] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL")); case_id: Mapped[str | None] = mapped_column(ForeignKey("cases.id", ondelete="SET NULL")); job_type: Mapped[str] = mapped_column(String(80)); status: Mapped[str] = mapped_column(String(30), default="pending"); input_payload: Mapped[dict | None] = mapped_column(JSON); result_payload: Mapped[dict | None] = mapped_column(JSON); storage_key: Mapped[str | None] = mapped_column(String(500)); file_name: Mapped[str | None] = mapped_column(String(255)); error_message: Mapped[str | None] = mapped_column(Text)
