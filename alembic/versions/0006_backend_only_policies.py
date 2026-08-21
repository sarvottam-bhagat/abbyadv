"""Harden backend-only tables and add missing foreign-key indexes."""
from alembic import op

revision = "0006_backend_only_policies"
down_revision = "0005_schema_completion"
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute("REVOKE ALL ON TABLE public.alembic_version FROM anon, authenticated")
    op.execute("ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS alembic_version_no_api_access ON public.alembic_version")
    op.execute("CREATE POLICY alembic_version_no_api_access ON public.alembic_version FOR ALL TO anon, authenticated USING (false) WITH CHECK (false)")
    for table in ("chat_messages", "legal_sources", "legal_source_chunks"):
        op.execute(f"REVOKE ALL ON TABLE public.{table} FROM anon, authenticated")
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS chat_messages_no_api_access ON public.chat_messages")
    op.execute("CREATE POLICY chat_messages_no_api_access ON public.chat_messages FOR ALL TO anon, authenticated USING (false) WITH CHECK (false)")
    op.execute("DROP POLICY IF EXISTS legal_sources_no_api_access ON public.legal_sources")
    op.execute("CREATE POLICY legal_sources_no_api_access ON public.legal_sources FOR ALL TO anon, authenticated USING (false) WITH CHECK (false)")
    op.execute("DROP POLICY IF EXISTS legal_source_chunks_no_api_access ON public.legal_source_chunks")
    op.execute("CREATE POLICY legal_source_chunks_no_api_access ON public.legal_source_chunks FOR ALL TO anon, authenticated USING (false) WITH CHECK (false)")
    op.execute("REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM PUBLIC, anon, authenticated")
    for table, column in (
        ("action_items", "case_id"), ("action_items", "client_id"),
        ("case_documents", "client_id"), ("drafts", "client_id"),
        ("drafts", "case_id"), ("drafts", "scenario_id"),
        ("legal_events", "client_id"), ("legal_events", "case_id"),
        ("legal_scenarios", "client_id"), ("report_jobs", "client_id"),
        ("report_jobs", "case_id"), ("research_memos", "client_id"),
        ("research_memos", "case_id"),
    ):
        op.create_index(f"ix_{table}_{column}", table, [column], unique=False, if_not_exists=True)


def downgrade():
    pass
