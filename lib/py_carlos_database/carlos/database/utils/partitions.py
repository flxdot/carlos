"""This module contains functions to manage partitions in the Universal Data Model."""

__all__ = [
    "BucketPartition",
    "QuarterlyPartition",
    "MonthlyPartition",
    "YearlyPartition",
    "create_partition",
]

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import DeclarativeBase

from carlos.database.context import RequestContext
from carlos.database.error_handling import PostgresErrorCodes, is_postgres_error_code


@dataclass(slots=True, frozen=True)
class _Partition(ABC):
    table: type[DeclarativeBase]

    @property
    def base_table_name(self) -> str:
        """Returns full qualified name of the partitioned table."""

        full_table_name = ""
        if self.table.__table__.schema:
            full_table_name += self.table.__table__.schema + "."
        full_table_name += self.table.__tablename__
        return full_table_name

    @property
    @abstractmethod
    def partition_table_name(self) -> str:
        """Returns the full qualified name of the partition."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def lower_bound(self) -> str:
        """Returns the lower bound of the partition."""

    @property
    @abstractmethod
    def upper_bound(self) -> str:
        """Returns the lower bound of the partition."""


@dataclass(slots=True, frozen=True)
class QuarterlyPartition(_Partition):
    """Represents a database partition."""

    year: int
    quarter: int

    @property
    def partition_table_name(self) -> str:
        """Returns the full qualified name of the partition."""

        return self.base_table_name + f"_y{self.year}q{self.quarter}"

    @property
    def lower_bound(self) -> str:
        """Returns the lower bound of the partition."""

        return f"'{date(self.year, (self.quarter - 1) * 3 + 1, 1).isoformat()}'"

    @property
    def upper_bound(self) -> str:
        """Returns the upper bound of the partition."""

        month = self.quarter * 3 + 1
        year = self.year
        if month > 12:
            month = 1
            year += 1

        return f"'{date(year, month, 1).isoformat()}'"

    @classmethod
    def from_timestamp(
        cls, timestamp: datetime, table: type[DeclarativeBase]
    ) -> "QuarterlyPartition":
        """Creates a new partition from a year and month."""

        quarter = (timestamp.month - 1) // 3 + 1
        return cls(year=timestamp.year, quarter=quarter, table=table)


@dataclass(slots=True, frozen=True)
class BucketPartition(_Partition):
    """Defines a partition that is divided into partitions every bucket_size id."""

    actual_id: int
    bucket_size: int

    def __post_init__(self):
        if self.bucket_size < 1:
            raise ValueError("bucket_size must be greater than 0")

    @property
    def partition_no(self) -> int:
        """Returns the base id of the partition."""

        return self.actual_id // self.bucket_size

    @property
    def partition_table_name(self) -> str:
        """Returns the full qualified name of the partition."""

        break_points = [
            (1_000_000, "m"),
            (1000, "k"),
        ]
        table_suffix = f"{self.lower_bound}_{self.upper_bound}"
        for break_point, suffix in break_points:
            if self.bucket_size >= break_point and self.bucket_size % break_point == 0:
                table_suffix = (
                    f"{self.lower_bound_int // break_point:04d}{suffix}"
                    f"_"
                    f"{self.upper_bound_int // break_point:04d}{suffix}"
                )
                break

        return f"{self.base_table_name}_{table_suffix.lower()}"

    @property
    def lower_bound_int(self) -> int:
        """Returns the lower bound of the partition as integert."""

        return self.partition_no * self.bucket_size

    @property
    def upper_bound_int(self) -> int:
        """Returns the upper bound of the partition as integer."""

        return (self.partition_no + 1) * self.bucket_size

    @property
    def lower_bound(self) -> str:
        """Returns the lower bound of the partition."""

        return str(self.lower_bound_int)

    @property
    def upper_bound(self) -> str:
        """Returns the upper bound of the partition."""

        return str(self.upper_bound_int)


@dataclass(slots=True, frozen=True)
class YearlyPartition(_Partition):
    """Defines a partition that is divided into partitions every year."""

    year: int

    @property
    def partition_table_name(self) -> str:
        """Returns the full qualified name of the partition."""

        return self.base_table_name + f"_y{self.year}"

    @property
    def lower_bound(self) -> str:
        """Returns the lower bound of the partition."""

        return f"'{date(self.year, 1, 1).isoformat()}'"

    @property
    def upper_bound(self) -> str:
        """Returns the upper bound of the partition."""

        return f"'{date(self.year + 1, 1, 1).isoformat()}'"

    @classmethod
    def from_timestamp(
        cls, timestamp: datetime, table: type[DeclarativeBase]
    ) -> "YearlyPartition":
        """Creates a new partition from a year and month."""

        return cls(year=timestamp.year, table=table)


@dataclass(slots=True, frozen=True)
class MonthlyPartition(_Partition):
    """Defines a partition that is divided into partitions every month."""

    year: int
    month: int

    @property
    def partition_table_name(self) -> str:
        """Returns the full qualified name of the partition."""

        return self.base_table_name + f"_y{self.year}m{self.month}"

    @property
    def lower_bound(self) -> str:
        """Returns the lower bound of the partition."""

        return f"'{date(self.year, self.month, 1).isoformat()}'"

    @property
    def upper_bound(self) -> str:
        """Returns the upper bound of the partition."""

        month = self.month + 1
        year = self.year
        if month > 12:
            month = 1
            year += 1

        return f"'{date(year, month, 1).isoformat()}'"

    @classmethod
    def from_timestamp(
        cls, timestamp: datetime, table: type[DeclarativeBase]
    ) -> "MonthlyPartition":
        """Creates a new partition from a year and month."""

        return cls(year=timestamp.year, month=timestamp.month, table=table)


Partition = YearlyPartition | QuarterlyPartition | MonthlyPartition | BucketPartition


async def create_partition(context: RequestContext, partition: Partition):
    """Creates the timeseries partitions for the current year and the next year."""

    schema, table_name = partition.partition_table_name.split(".")

    if await does_table_exist(
        context=context,
        schema_name=schema,
        table_name=table_name,
    ):
        return

    statement = text(
        f"CREATE TABLE {partition.partition_table_name} "
        f"PARTITION OF {partition.base_table_name} "
        f"FOR VALUES FROM ({partition.lower_bound}) "
        f"TO ({partition.upper_bound});"
    )
    try:
        await context.connection.execute(statement)
        await context.connection.commit()
    except ProgrammingError as ex:  # pragma: no cover
        if is_postgres_error_code(ex, PostgresErrorCodes.DUPLICATE_TABLE):
            await context.connection.rollback()
            # seems like another worker already created the table
            return
        raise


async def does_table_exist(
    context: RequestContext, schema_name: str, table_name: str
) -> bool:
    """Checks if a table exists."""

    statement = text(
        "SELECT EXISTS ("
        "SELECT FROM information_schema.tables "
        f"WHERE table_schema = '{schema_name}' "
        f"AND table_name = '{table_name}');"
    )
    return bool((await context.connection.execute(statement)).scalar())
