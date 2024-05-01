from datetime import UTC, datetime

from ..orm import TimeseriesOrm
from .partitions import QuarterlyPartition


class TestQuarterlyDatabasePartition:
    def test_properties(self):
        """Ensures that the properties are calculated correctly."""

        partition = QuarterlyPartition.from_timestamp(
            timestamp=datetime(2021, 11, 3, 14, 54, 23, 22222, tzinfo=UTC),
            table=TimeseriesOrm,
        )

        assert partition.base_table_name == "data.timeseries"
        assert partition.partition_table_name == "data.timeseries_y2021q4"
        assert partition.lower_bound == "'2021-10-01'"
        assert partition.upper_bound == "'2022-01-01'"

    def test_hash(self):
        """Ensures that the hash is the same for 2 dates in the same quater."""

        partition = QuarterlyPartition.from_timestamp(
            timestamp=datetime(2021, 11, 3, 14, 54, 23, 22222, tzinfo=UTC),
            table=TimeseriesOrm,
        )

        second_partition = QuarterlyPartition.from_timestamp(
            timestamp=datetime(2021, 11, 6, 14, 54, 23, 22222, tzinfo=UTC),
            table=TimeseriesOrm,
        )

        assert hash(partition) == hash(second_partition)
