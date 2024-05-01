from datetime import UTC, datetime

import pytest

from ..orm import TimeseriesOrm
from .partitions import (
    BucketPartition,
    MonthlyPartition,
    QuarterlyPartition,
    YearlyPartition,
)


class TestYearlyPartition:
    def test_properties(self):
        """Ensures that the properties are calculated correctly."""

        partition = YearlyPartition.from_timestamp(
            timestamp=datetime(2021, 12, 3, 14, 54, 23, 22222, tzinfo=UTC),
            table=TimeseriesOrm,
        )

        assert partition.base_table_name == "carlos.timeseries"
        assert partition.partition_table_name == "carlos.timeseries_y2021"
        assert partition.lower_bound == "'2021-01-01'"
        assert partition.upper_bound == "'2022-01-01'"

    def test_hash(self):
        """Ensures that the hash is the same for 2 dates in the same quater."""

        partition = YearlyPartition.from_timestamp(
            timestamp=datetime(2021, 11, 3, 14, 54, 23, 22222, tzinfo=UTC),
            table=TimeseriesOrm,
        )

        second_partition = YearlyPartition.from_timestamp(
            timestamp=datetime(2021, 11, 6, 14, 54, 23, 22222, tzinfo=UTC),
            table=TimeseriesOrm,
        )

        assert hash(partition) == hash(second_partition)


class TestQuarterlyPartition:
    def test_properties(self):
        """Ensures that the properties are calculated correctly."""

        partition = QuarterlyPartition.from_timestamp(
            timestamp=datetime(2021, 12, 3, 14, 54, 23, 22222, tzinfo=UTC),
            table=TimeseriesOrm,
        )

        assert partition.base_table_name == "carlos.timeseries"
        assert partition.partition_table_name == "carlos.timeseries_y2021q4"
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


class TestMonthlyPartition:
    def test_properties(self):
        """Ensures that the properties are calculated correctly."""

        partition = MonthlyPartition.from_timestamp(
            timestamp=datetime(2021, 12, 3, 14, 54, 23, 22222, tzinfo=UTC),
            table=TimeseriesOrm,
        )

        assert partition.base_table_name == "carlos.timeseries"
        assert partition.partition_table_name == "carlos.timeseries_y2021m12"
        assert partition.lower_bound == "'2021-12-01'"
        assert partition.upper_bound == "'2022-01-01'"

    def test_hash(self):
        """Ensures that the hash is the same for 2 dates in the same quater."""

        partition = MonthlyPartition.from_timestamp(
            timestamp=datetime(2021, 11, 3, 14, 54, 23, 22222, tzinfo=UTC),
            table=TimeseriesOrm,
        )

        second_partition = MonthlyPartition.from_timestamp(
            timestamp=datetime(2021, 11, 6, 14, 54, 23, 22222, tzinfo=UTC),
            table=TimeseriesOrm,
        )

        assert hash(partition) == hash(second_partition)


class TestBucketPartition:
    @pytest.mark.parametrize(
        "actual_id, bucket_size, expected_lower_bound, expected_upper_bound, "
        "expected_table_suffix",
        [
            pytest.param(123_456, 1000, 123_000, 124_000, "0123k_0124k", id="thousand"),
            pytest.param(
                123_456, 10_000, 120_000, 130_000, "0120k_0130k", id="ten-thousand"
            ),
            pytest.param(
                123_456, 20_000, 120_000, 140_000, "0120k_0140k", id="twenty-thousand"
            ),
            pytest.param(
                123_456, 25_000, 100_000, 125_000, "0100k_0125k", id="twenty-thousand"
            ),
            pytest.param(
                123_456, 1_000_000, 0, 1_000_000, "0000m_0001m", id="first-million"
            ),
            pytest.param(
                1_234_567,
                1_000_000,
                1_000_000,
                2_000_000,
                "0001m_0002m",
                id="second-million",
            ),
            pytest.param(53_000, 42_069, 42_069, 84_138, "42069_84138", id="random"),
        ],
    )
    def test_properties(
        self,
        actual_id: int,
        bucket_size: int,
        expected_lower_bound: int,
        expected_upper_bound: int,
        expected_table_suffix: str,
    ):
        """Ensures that the bucket partition properties are calculated correctly."""
        partition = BucketPartition(
            actual_id=actual_id,
            table=TimeseriesOrm,
            bucket_size=bucket_size,
        )

        assert partition.base_table_name == "carlos.timeseries"
        assert (
            partition.partition_table_name
            == f"carlos.timeseries_{expected_table_suffix}"
        )
        assert int(partition.lower_bound) == expected_lower_bound
        assert int(partition.upper_bound) == expected_upper_bound

    def test_validation(self):
        """Ensures that the bucket size is validated correctly."""

        with pytest.raises(ValueError):
            BucketPartition(
                actual_id=123_456,
                table=TimeseriesOrm,
                bucket_size=0,
            )
