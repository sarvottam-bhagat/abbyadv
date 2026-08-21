"""Add general legal client profile fields."""
from alembic import op
import sqlalchemy as sa

revision = "0007_client_legal_profile"
down_revision = "0006_backend_only_policies"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    columns = {
        "alternate_phone": sa.String(50), "address": sa.Text(), "postal_code": sa.String(20),
        "date_of_birth": sa.Date(), "occupation": sa.String(150), "id_type": sa.String(50),
        "id_number": sa.String(100), "preferred_contact_method": sa.String(30),
        "organization_name": sa.String(250), "referred_by": sa.String(200),
    }
    existing = {item["name"] for item in sa.inspect(bind).get_columns("clients")}
    for name, column in columns.items():
        if name not in existing:
            op.add_column("clients", sa.Column(name, column, nullable=True))


def downgrade():
    pass
