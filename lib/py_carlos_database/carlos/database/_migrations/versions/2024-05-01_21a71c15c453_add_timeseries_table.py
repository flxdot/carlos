"""add timeseries table

Revision ID: 21a71c15c453
Revises: cc68eca3644d
Create Date: 2024-05-01 10:00:52.135019

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "21a71c15c453"
down_revision = "cc68eca3644d"
branch_labels = None
depends_on = None


def upgrade():
    timeseries_ddl = """
        CREATE TABLE carlos.timeseries (
            timestamp_utc TIMESTAMP WITH TIME ZONE NOT NULL,
            timeseries_id INTEGER REFERENCES carlos.device_signal(timeseries_id)
                ON DELETE CASCADE NOT NULL,
            value REAL,
            PRIMARY KEY (timeseries_id, timestamp_utc)
        ) PARTITION BY RANGE (timestamp_utc);
        CREATE INDEX ON carlos.timeseries (timeseries_id);
        CREATE INDEX ON carlos.timeseries (timestamp_utc);
        COMMENT ON TABLE carlos.timeseries IS
            'Holds all numeric and boolean timeseries data.';
        COMMENT ON COLUMN carlos.timeseries.timestamp_utc IS
            'The timestamp of the data point in UTC.';
        COMMENT ON COLUMN carlos.timeseries.timeseries_id IS
            'The unique identifier series.';
        COMMENT ON COLUMN carlos.timeseries.value IS
            'The value of the data point.';
        """
    op.execute(timeseries_ddl)


def downgrade():
    op.execute("DROP TABLE carlos.timeseries;")
