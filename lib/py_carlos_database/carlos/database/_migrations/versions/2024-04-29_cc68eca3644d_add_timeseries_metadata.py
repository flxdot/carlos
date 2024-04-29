"""add timeseries metadata

Revision ID: cc68eca3644d
Revises: a035faa3c7d7
Create Date: 2024-04-29 19:17:40.883900

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "cc68eca3644d"
down_revision = "a035faa3c7d7"
branch_labels = None
depends_on = None


def upgrade():
    driver_ddl = """
        CREATE TABLE carlos.device_driver (
            device_id UUID NOT NULL
                REFERENCES carlos.device(device_id) ON DELETE CASCADE,
            driver_identifier VARCHAR(64) NOT NULL,
            direction VARCHAR(32) NOT NULL,
            driver_module VARCHAR(255) NOT NULL,
            display_name VARCHAR(255) NOT NULL,
            is_visible_on_dashboard BOOLEAN NOT NULL,
            PRIMARY KEY (device_id, driver_identifier)
        );
        COMMENT ON TABLE carlos.device_driver IS 'Contains the metadata for a given driver of a device.';
        COMMENT ON COLUMN carlos.device_driver.device_id IS 'The device the driver belongs to.';
        COMMENT ON COLUMN carlos.device_driver.driver_identifier IS 'The unique identifier of the driver in the context of the device.';
        COMMENT ON COLUMN carlos.device_driver.direction IS 'The direction of the IO.';
        COMMENT ON COLUMN carlos.device_driver.driver_module IS 'The module that implements the IO driver.';
        COMMENT ON COLUMN carlos.device_driver.display_name IS 'The name of the driver that is displayed in the UI.';
        COMMENT ON COLUMN carlos.device_driver.is_visible_on_dashboard IS 'Whether the driver is visible on the dashboard.';
    """
    op.execute(driver_ddl)

    signal_ddl = """
        CREATE TABLE carlos.device_signal (
            timeseries_id SERIAL PRIMARY KEY,
            device_id UUID NOT NULL,
            driver_identifier VARCHAR(64) NOT NULL,
            signal_identifier VARCHAR(64) NOT NULL,
            display_name VARCHAR(255) NOT NULL,
            unit_of_measurement SMALLINT NOT NULL,
            is_visible_on_dashboard BOOLEAN NOT NULL,
            FOREIGN KEY (device_id, driver_identifier)
                REFERENCES carlos.device_driver(device_id, driver_identifier) ON DELETE CASCADE,
            UNIQUE (device_id, driver_identifier, signal_identifier)
        );
        COMMENT ON TABLE carlos.device_signal IS 'Contains the metadata for a given signal of a driver.';
        COMMENT ON COLUMN carlos.device_signal.timeseries_id IS 'The unique identifier of the signal.';
        COMMENT ON COLUMN carlos.device_signal.device_id IS 'The device the signal belongs to.';
        COMMENT ON COLUMN carlos.device_signal.driver_identifier IS 'The driver the signal belongs to.';
        COMMENT ON COLUMN carlos.device_signal.signal_identifier IS 'The unique identifier of the signal in the context of the driver.';
        COMMENT ON COLUMN carlos.device_signal.display_name IS 'The name of the signal that is displayed in the UI.';
        COMMENT ON COLUMN carlos.device_signal.unit_of_measurement IS 'The unit of measurement of the driver.';
        COMMENT ON COLUMN carlos.device_signal.is_visible_on_dashboard IS 'Whether the signal is visible on the dashboard.';
    """
    op.execute(signal_ddl)


def downgrade():
    op.execute("DROP TABLE carlos.device_signal;")
    op.execute("DROP TABLE carlos.device_driver;")
