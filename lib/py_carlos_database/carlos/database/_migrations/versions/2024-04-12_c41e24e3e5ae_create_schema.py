"""create schema

Revision ID: c41e24e3e5ae
Revises: 
Create Date: 2024-04-12 16:16:02.321702

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c41e24e3e5ae"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(sa.text("CREATE SCHEMA carlos;"))


def downgrade():
    op.execute(sa.text("DROP SCHEMA carlos CASCADE;"))
