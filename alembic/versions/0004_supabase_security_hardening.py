"""Correct ownership policies for internal user IDs and provision private Storage."""
from alembic import op

revision = "0004_supabase_security_hardening"
down_revision = "0003_abbyy_processing"
branch_labels = None
depends_on = None

USER_TABLES = ("clients", "cases", "case_documents", "document_chunks", "chat_sessions", "legal_scenarios", "drafts", "research_memos", "legal_events", "action_items", "report_jobs")

def upgrade():
    if op.get_bind().dialect.name != "postgresql": return
    for table in USER_TABLES:
        op.execute(f"DROP POLICY IF EXISTS {table}_owner_all ON public.{table}")
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"""CREATE POLICY {table}_owner_all ON public.{table} FOR ALL TO authenticated
          USING (EXISTS (SELECT 1 FROM public.users owner WHERE owner.id = {table}.user_id AND owner.auth_user_id = (SELECT auth.uid())::text))
          WITH CHECK (EXISTS (SELECT 1 FROM public.users owner WHERE owner.id = {table}.user_id AND owner.auth_user_id = (SELECT auth.uid())::text))""")
        op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON public.{table} TO authenticated")
    op.execute("DROP POLICY IF EXISTS case_parties_owner_all ON public.case_parties")
    op.execute("ALTER TABLE public.case_parties ENABLE ROW LEVEL SECURITY")
    op.execute("""CREATE POLICY case_parties_owner_all ON public.case_parties FOR ALL TO authenticated
      USING (EXISTS (SELECT 1 FROM public.cases c JOIN public.users owner ON owner.id = c.user_id WHERE c.id = case_parties.case_id AND owner.auth_user_id = (SELECT auth.uid())::text))
      WITH CHECK (EXISTS (SELECT 1 FROM public.cases c JOIN public.users owner ON owner.id = c.user_id WHERE c.id = case_parties.case_id AND owner.auth_user_id = (SELECT auth.uid())::text))""")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON public.case_parties TO authenticated")
    op.execute("ALTER TABLE public.users ENABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS users_owner_select ON public.users")
    op.execute("DROP POLICY IF EXISTS users_owner_update ON public.users")
    op.execute("DROP POLICY IF EXISTS users_owner_insert ON public.users")
    op.execute("CREATE POLICY users_owner_select ON public.users FOR SELECT TO authenticated USING (auth_user_id = (SELECT auth.uid())::text)")
    op.execute("CREATE POLICY users_owner_update ON public.users FOR UPDATE TO authenticated USING (auth_user_id = (SELECT auth.uid())::text) WITH CHECK (auth_user_id = (SELECT auth.uid())::text)")
    op.execute("CREATE POLICY users_owner_insert ON public.users FOR INSERT TO authenticated WITH CHECK (auth_user_id = (SELECT auth.uid())::text)")
    op.execute("GRANT SELECT, INSERT, UPDATE ON public.users TO authenticated")
    op.execute("""INSERT INTO storage.buckets (id, name, public)
      VALUES ('case-documents', 'case-documents', false)
      ON CONFLICT (id) DO UPDATE SET public = false""")
    op.execute("DROP POLICY IF EXISTS case_documents_insert ON storage.objects")
    op.execute("DROP POLICY IF EXISTS case_documents_select ON storage.objects")
    op.execute("DROP POLICY IF EXISTS case_documents_update ON storage.objects")
    op.execute("DROP POLICY IF EXISTS case_documents_delete ON storage.objects")
    op.execute("""CREATE POLICY case_documents_insert ON storage.objects FOR INSERT TO authenticated
      WITH CHECK (bucket_id = 'case-documents' AND (storage.foldername(name))[1] = (SELECT auth.uid())::text)""")
    op.execute("""CREATE POLICY case_documents_select ON storage.objects FOR SELECT TO authenticated
      USING (bucket_id = 'case-documents' AND (storage.foldername(name))[1] = (SELECT auth.uid())::text)""")
    op.execute("""CREATE POLICY case_documents_update ON storage.objects FOR UPDATE TO authenticated
      USING (bucket_id = 'case-documents' AND (storage.foldername(name))[1] = (SELECT auth.uid())::text)
      WITH CHECK (bucket_id = 'case-documents' AND (storage.foldername(name))[1] = (SELECT auth.uid())::text)""")
    op.execute("""CREATE POLICY case_documents_delete ON storage.objects FOR DELETE TO authenticated
      USING (bucket_id = 'case-documents' AND (storage.foldername(name))[1] = (SELECT auth.uid())::text)""")

def downgrade():
    if op.get_bind().dialect.name != "postgresql": return
    for name in ("case_documents_insert", "case_documents_select", "case_documents_update", "case_documents_delete"):
        op.execute(f"DROP POLICY IF EXISTS {name} ON storage.objects")

