"""Allow chat-only documents without a matter."""
from alembic import op
import sqlalchemy as sa


revision = "0008_generic_chat_files"
down_revision = "0007_client_legal_profile"
branch_labels = None
depends_on = None


def upgrade():
    column = next(item for item in sa.inspect(op.get_bind()).get_columns("case_documents") if item["name"] == "case_id")
    if not column["nullable"]:
        op.alter_column("case_documents", "case_id", existing_type=sa.String(length=36), nullable=True)


def downgrade():
    pass
