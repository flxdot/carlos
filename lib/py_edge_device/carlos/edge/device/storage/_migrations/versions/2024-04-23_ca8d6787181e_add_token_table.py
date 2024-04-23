"""add token table

Revision ID: ca8d6787181e
Revises: 
Create Date: 2024-04-23 21:06:00.273576

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "ca8d6787181e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    token_table_ddl = """
    CREATE TABLE api_token (
        token VARCHAR(4096),
        valid_until_utc CHAR(26)
    );
    """
    op.execute(token_table_ddl)


def downgrade():
    op.execute("DROP TABLE api_token;")
