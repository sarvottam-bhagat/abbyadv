"""Enable ownership RLS for Supabase Postgres deployments."""
from alembic import op

revision = "0002_supabase_rls"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

TABLES = ("users", "clients", "cases", "case_documents", "chat_sessions", "legal_scenarios", "drafts", "research_memos", "legal_events", "action_items", "report_jobs")

def upgrade():
    if op.get_bind().dialect.name != "postgresql": return
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        if table == "users":
            op.execute("CREATE POLICY users_owner_select ON users FOR SELECT TO authenticated USING (auth.uid()::text = auth_user_id)")
            op.execute("CREATE POLICY users_owner_update ON users FOR UPDATE TO authenticated USING (auth.uid()::text = auth_user_id) WITH CHECK (auth.uid()::text = auth_user_id)")
        else:
            op.execute(f"CREATE POLICY {table}_owner_all ON {table} FOR ALL TO authenticated USING ((select auth.uid()::text) = user_id) WITH CHECK ((select auth.uid()::text) = user_id)")

def downgrade():
    if op.get_bind().dialect.name != "postgresql": return
    for table in reversed(TABLES):
        op.execute(f"DROP POLICY IF EXISTS {table}_owner_all ON {table}")
        if table == "users":
            op.execute("DROP POLICY IF EXISTS users_owner_select ON users")
            op.execute("DROP POLICY IF EXISTS users_owner_update ON users")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

