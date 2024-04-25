"""add tables to store timeseries

Revision ID: 476f88fe4d1b
Revises: ca8d6787181e
Create Date: 2024-04-25 18:48:06.176408

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "476f88fe4d1b"
down_revision = "ca8d6787181e"
branch_labels = None
depends_on = None


def upgrade():
    timeseries_index_ddl = """
    CREATE TABLE timeseries_index (
        timeseries_id INTEGER PRIMARY KEY,
        driver_identifier VARCHAR(64) NOT NULL,
        driver_signal VARCHAR(64) NOT NULL,
        server_timeseries_id INTEGER NULL,
        UNIQUE(driver_identifier, driver_signal)
    );
    """
    op.execute(timeseries_index_ddl)

    timeseries_data_ddl = """
    CREATE TABLE timeseries_data (
        timeseries_id INTEGER NOT NULL,
        timestamp_utc INTEGER NOT NULL,
        value FLOAT NOT NULL,
        staging_id VARCHAR(4) NULL,
        staged_at_utc INTEGER NULL,
        PRIMARY KEY(timeseries_id, timestamp_utc),
        FOREIGN KEY(timeseries_id) REFERENCES timeseries_index(timeseries_id)
    );
    """
    op.execute(timeseries_data_ddl)


def downgrade():
    op.execute("DROP TABLE timeseries_data;")
    op.execute("DROP TABLE timeseries_index;")
