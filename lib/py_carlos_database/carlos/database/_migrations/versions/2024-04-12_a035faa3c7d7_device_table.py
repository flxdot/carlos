"""device table

Revision ID: a035faa3c7d7
Revises: c41e24e3e5ae
Create Date: 2024-04-12 16:17:03.936903

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a035faa3c7d7"
down_revision = "c41e24e3e5ae"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        sa.text(
            """
        CREATE TABLE carlos.device (
            device_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            display_name VARCHAR(255) NOT NULL,
            description TEXT,
            registered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
            last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
        );
        COMMENT ON TABLE carlos.device IS 'Contains all known devices for the tenant.';
        COMMENT ON COLUMN carlos.device.device_id IS 'The unique identifier of the device.';
        COMMENT ON COLUMN carlos.device.display_name IS 'The name of the device that is displayed to the user.';
        COMMENT ON COLUMN carlos.device.description IS 'A description of the device for the user.';
        COMMENT ON COLUMN carlos.device.registered_at IS 'The date and time when the device was registered.';
        COMMENT ON COLUMN carlos.device.last_seen_at IS 'The date and time when the server last received data from the device.';
        """
        )
    )


def downgrade():
    op.execute(sa.text("DROP TABLE carlos.device CASCADE;"))
