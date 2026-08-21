"""Backfill columns/tables introduced after the initial scaffold."""
from alembic import op
import sqlalchemy as sa
from src.database.base import Base
from src.database import models  # noqa: F401

revision = "0005_schema_completion"
down_revision = "0004_supabase_security_hardening"
branch_labels = None
depends_on = None

def _columns(table): return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}
def _add(table, name, column):
    if name not in _columns(table): op.add_column(table, sa.Column(name, column, nullable=True))

def upgrade():
    Base.metadata.create_all(bind=op.get_bind())
    for name, column in {
        "file_type":sa.String(80), "storage_bucket":sa.String(120), "ocr_status":sa.String(30), "embedding_status":sa.String(30), "abbyy_transaction_id":sa.String(200), "summary":sa.Text(), "extracted_facts":sa.JSON(), "ocr_metadata":sa.JSON(), "page_count":sa.Integer(), "confidence_score":sa.Float(), "error_message":sa.Text(),
    }.items(): _add("case_documents", name, column)
    for name, column in {"mode":sa.String(30), "context_meta":sa.JSON()}.items(): _add("chat_sessions", name, column)
    for name, column in {"error_message":sa.Text(), "tool_trace":sa.JSON(), "citations":sa.JSON()}.items(): _add("chat_messages", name, column)
    for name, column in {"description":sa.Text(), "country":sa.String(2), "state":sa.String(100), "scenario_type":sa.String(80), "uploaded_document_ids":sa.JSON(), "execution_status":sa.String(30), "error_message":sa.Text(), "tool_trace":sa.JSON(), "citations":sa.JSON(), "is_template":sa.Boolean()}.items(): _add("legal_scenarios", name, column)
    for name, column in {"content_md":sa.Text(), "content_html":sa.Text(), "source_prompt":sa.Text(), "input_context":sa.JSON(), "citations":sa.JSON(), "version":sa.Integer()}.items(): _add("drafts", name, column)
    for name, column in {"title":sa.String(250), "research_type":sa.String(80), "sources":sa.JSON(), "tool_trace":sa.JSON()}.items(): _add("research_memos", name, column)
    for name, column in {"source":sa.String(30), "start_date":sa.Date(), "end_date":sa.Date(), "is_reviewed":sa.Boolean(), "reviewed_at":sa.DateTime(timezone=True), "description":sa.Text(), "metadata_json":sa.JSON()}.items(): _add("legal_events", name, column)

def downgrade():
    pass

