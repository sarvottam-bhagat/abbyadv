"""Track ABBYY transaction state for document OCR."""
from alembic import op
import sqlalchemy as sa
revision = "0003_abbyy_processing"
down_revision = "0002_supabase_rls"
branch_labels = None
depends_on = None
def upgrade():
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("case_documents")}
    if "abbyy_transaction_id" not in columns:
        op.add_column("case_documents", sa.Column("abbyy_transaction_id", sa.String(length=200), nullable=True))
    indexes = {index["name"] for index in sa.inspect(bind).get_indexes("case_documents")}
    if "ix_case_documents_abbyy_transaction_id" not in indexes:
        op.create_index("ix_case_documents_abbyy_transaction_id", "case_documents", ["abbyy_transaction_id"])
def downgrade():
    op.drop_index("ix_case_documents_abbyy_transaction_id", table_name="case_documents")
    op.drop_column("case_documents", "abbyy_transaction_id")
