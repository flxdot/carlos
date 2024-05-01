import builtins
import types
from abc import abstractmethod
from contextlib import asynccontextmanager, contextmanager
from datetime import date, datetime
from functools import partial
from typing import AsyncIterator, Generator, Sequence

import pytest
import pytest_asyncio
from _pytest.fixtures import FixtureRequest
from _pytest.mark import ParameterSet
from carlos.edge.interface.device import DriverDirection
from carlos.edge.interface.units import UnitOfMeasurement
from devtools.converter import to_environment
from devtools.docker import ContainerHandler, ContainerManager, PostgresContainer
from devtools.networking import find_next_unused_port
from devtools.testing import setup_test_environment
from pydantic.alias_generators import to_snake
from sqlalchemy import Column, Engine, Table
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from carlos.database.config import DatabaseConnectionSettings
from carlos.database.connection import (
    get_async_carlos_database_engine,
    get_carlos_database_engine,
)
from carlos.database.context import RequestContext
from carlos.database.device import (
    CarlosDeviceDriver,
    CarlosDeviceDriverCreate,
    CarlosDeviceSignal,
    CarlosDeviceSignalCreate,
    create_device_driver,
    create_device_signals,
    delete_device_driver,
)
from carlos.database.migration import setup_test_db_data
from carlos.database.testing.expectations import DeviceId

connection_settings = DatabaseConnectionSettings(
    host="localhost",
    port=find_next_unused_port(2347),
    name="postgres",
    user="postgres",
    password="postgres",
)


@pytest.fixture(scope="session", name="carlos_db_test_environment")
def fixture_test_environment():
    """Fixture to set up the temporary docker test database with test data"""

    container_handler = ContainerHandler(
        container=PostgresContainer(
            name="carlos-pytest-db",
            port=connection_settings.port,
            database_name=connection_settings.name,
            user=connection_settings.user,
            password=connection_settings.password.get_secret_value(),
        ),
        post_setup=partial(setup_test_db_data, connection_settings=connection_settings),
    )

    container_manager = ContainerManager(container_handlers=[container_handler])

    environment = to_environment(connection_settings)

    with setup_test_environment(
        container_manager=container_manager,
        environment=environment,
    ):
        yield


@contextmanager
def new_engine() -> Generator[Engine, None, None]:
    """Provides a global (sync) engine to the test database"""

    engine = get_carlos_database_engine(connection_settings=connection_settings)
    try:
        yield engine
    finally:
        engine.dispose()


@asynccontextmanager
async def new_async_engine() -> AsyncIterator[AsyncEngine]:
    """Provides a global async engine to the test database"""

    async_engine = get_async_carlos_database_engine(
        connection_settings=connection_settings,
    )
    try:
        yield async_engine
    finally:
        await async_engine.dispose()


@pytest_asyncio.fixture(name="async_carlos_db_engine")
async def fixture_async_engine() -> AsyncIterator[AsyncEngine]:
    """Provides a global async engine to the test database"""
    async with new_async_engine() as async_engine_:
        yield async_engine_


@pytest_asyncio.fixture(name="async_carlos_db_connection")
async def fixture_async_connection(
    async_carlos_db_engine: AsyncEngine,
) -> AsyncIterator[AsyncConnection]:
    """Provides a fresh async connection to the test database from the connection
    pool"""
    async with async_carlos_db_engine.connect() as conn:
        yield conn


@pytest_asyncio.fixture(name="async_carlos_db_context")
async def fixture_async_context(
    async_carlos_db_connection: AsyncConnection,
) -> AsyncIterator[RequestContext]:
    """Provides a fresh async connection to the test database from the connection
    pool"""
    yield RequestContext(connection=async_carlos_db_connection)


@pytest_asyncio.fixture()
async def driver(
    async_carlos_db_context: RequestContext,
) -> AsyncIterator[CarlosDeviceDriver]:

    device_id = DeviceId.DEVICE_A.value

    to_create = CarlosDeviceDriverCreate(
        display_name="My Driver",
        is_visible_on_dashboard=True,
        driver_identifier="my-driver",
        direction=DriverDirection.INPUT,
        driver_module="does_not_matter",
    )

    created = await create_device_driver(
        context=async_carlos_db_context, device_id=device_id, driver=to_create
    )

    yield created

    # cleanup: delete the driver
    await delete_device_driver(
        context=async_carlos_db_context,
        device_id=device_id,
        driver_identifier=created.driver_identifier,
    )


@pytest_asyncio.fixture()
async def driver_signals(
    async_carlos_db_context: RequestContext, driver: CarlosDeviceDriver
) -> AsyncIterator[list[CarlosDeviceSignal]]:

    to_create = [
        CarlosDeviceSignalCreate(
            display_name="Temperature",
            unit_of_measurement=UnitOfMeasurement.CELSIUS,
            is_visible_on_dashboard=True,
            signal_identifier="temperature",
        ),
        CarlosDeviceSignalCreate(
            display_name="Humidity",
            unit_of_measurement=UnitOfMeasurement.HUMIDITY_PERCENTAGE,
            is_visible_on_dashboard=True,
            signal_identifier="humidity",
        ),
    ]

    created = await create_device_signals(
        context=async_carlos_db_context,
        device_id=driver.device_id,
        driver_identifier=driver.driver_identifier,
        signals=to_create,
    )

    yield created

    # no cleanup. It will be removed with the teardown of driver fixture


def format_any_of(expected: Sequence[str]) -> str:  # pragma: no cover
    """Formats a collection of strings in a human-readable way."""

    if len(expected) == 1:
        return f"{expected[0]}"

    return f"{', '.join(expected[:-1])} or {expected[-1]}"


class GuidelineTesterVisitor:
    """Visitor to check if all resources have a comment."""

    @abstractmethod
    def visit(self, resource: Table | Column) -> None:
        """Visit a resource."""
        raise NotImplementedError()


class ResourceHasComment(GuidelineTesterVisitor):
    """Ensures that all resources have a comment."""

    def visit(self, resource: Table | Column):
        """Visit a resource."""

        assert (
            resource.comment
        ), f"{resource.__class__.__name__} {resource} has no comment."

        assert (
            resource.comment.strip()
        ), f"{resource.__class__.__name__} {resource} comment is empty."


class ResourceCommentEndsWithPeriod(GuidelineTesterVisitor):
    """Ensures that all resources have a comment that ends with a period."""

    def visit(self, resource: Table | Column):
        """Visit a resource."""

        if resource.comment is None:  # pragma: no cover
            raise ValueError("Resource has no comment.")

        assert resource.comment.endswith("."), (
            f"{resource.__class__.__name__} {resource} has a comment that does "
            "not end with a period."
        )


class ResourceNameIsSnakeCase(GuidelineTesterVisitor):
    """Ensures that all resources have a snake case name."""

    def visit(self, resource: Table | Column):
        assert (
            to_snake(resource.name) == resource.name
        ), f"{resource.__class__.__name__} {resource} has no snake case name."


class PrimaryKeysHaveSuffix(GuidelineTesterVisitor):
    """Ensures that all primary keys follow the naming convention."""

    _EXCEPTIONS = (
        # revision may be part of a primary key, but does not require the suffix
        # as the naming is good enough
        "revision",
    )

    def visit(self, resource: Table | Column):
        if isinstance(resource, Column) and resource.primary_key:
            if len(resource.table.primary_key) == 1:
                assert self._is_column_valid(
                    resource
                ), f"PrimaryKey Column {resource} is missing mandatory '_id' suffix."
            else:  # pragma: no cover
                # For composite primary keys, we require at least one column to
                # end with _id
                assert any(
                    self._is_column_valid(pk_column)
                    for pk_column in resource.table.primary_key
                ), "At least one column of a composite primary key must end with '_id'."

    def _is_column_valid(self, column: Column) -> bool:
        """Checks if the column follows the expected naming scheme."""

        if column.type.python_type is datetime:  # pragma: no cover
            # if the primary key is a timestamp, we do not require the suffix
            return True

        if column.name in self._EXCEPTIONS:
            return True  # pragma: no cover

        return column.name.endswith("_id")


class ColumnTypeMatchesForeignKeyColumnType(GuidelineTesterVisitor):
    """Ensures that the types between the foreignkey column and the reference
    column match."""

    def visit(self, resource: Table | Column):
        if isinstance(resource, Column) and resource.foreign_keys:  # pragma: no cover
            assert len(resource.foreign_keys) == 1, (
                f"Column {resource} has more than one foreign key. "
                "This is not supported."
            )

            foreign_key = next(iter(resource.foreign_keys))

            assert isinstance(resource.type, type(foreign_key.column.type)), (
                f"Type of {resource} ({resource.type}) does not match its foreign key "
                f"{foreign_key.column} ({foreign_key.column.type})."
            )


class BooleanColumnHasPrefix(GuidelineTesterVisitor):
    """Ensures that all boolean columns follow the naming convention."""

    EXPECTED_PREFIXES = ("is_", "has_", "does_")

    def visit(self, resource: Table | Column):
        if (
            isinstance(resource, Column) and resource.type.python_type is bool
        ):  # pragma: no cover
            assert any(
                resource.name.startswith(prefix) for prefix in self.EXPECTED_PREFIXES
            ), (
                f"Column {resource} is missing mandatory "
                "'is_', 'has_' or 'does_' prefix."
            )


class DateTimeColumnsAreTimezoneAware(GuidelineTesterVisitor):
    """Ensures that all datetime columns are timezone aware."""

    def visit(self, resource: Table | Column):
        if isinstance(resource, Column) and resource.type.python_type is datetime:
            assert (
                resource.type.timezone  # type: ignore
            ), f"Column {resource} is not timezone aware."


class DateTimeColumnsHaveSuffix(GuidelineTesterVisitor):
    """Ensures that all datetime columns follow the naming convention."""

    EXPECTED_SUFFIXES = ("_at", "_from", "to", "_after", "_before")

    # some special column names that are named already in the correct way
    EXCEPTIONS = ["timestamp_utc"]

    def visit(self, resource: Table | Column):
        if (
            isinstance(resource, Column)
            and resource.type.python_type is datetime
            and resource.name not in self.EXCEPTIONS
        ):
            assert any(
                resource.name.endswith(suffix) for suffix in self.EXPECTED_SUFFIXES
            ), (
                f"Column {resource} is missing mandatory "
                f"{format_any_of(self.EXPECTED_SUFFIXES)} suffix."
            )


class DateColumnsHaveSuffix(GuidelineTesterVisitor):
    """Ensures that all date columns follow the naming convention."""

    EXPECTED_SUFFIXES = (
        "_at_date_utc",
        "_from_date_utc",
        "to_date_utc",
        "_after_date_utc",
        "_before_date_utc",
    )

    def visit(self, resource: Table | Column):  # pragma: no cover
        if isinstance(resource, Column) and resource.type.python_type is date:
            assert any(
                resource.name.endswith(suffix) for suffix in self.EXPECTED_SUFFIXES
            ), (
                f"Column {resource} is missing mandatory "
                f"{format_any_of(self.EXPECTED_SUFFIXES)} suffix."
            )


class TableNamesAreSingular(GuidelineTesterVisitor):
    """Ensures that all table names are singular."""

    EXCEPTIONS = (
        # singular words ending in s
        "series",
        # allowed plural words, because they do not reference the entity
        # as plural but a collection of things of that entity
        "settings",
        "properties",
    )

    def visit(self, resource: Table | Column):
        if isinstance(resource, Table):
            if resource.name.endswith("ss") or any(
                resource.name.endswith(exception) for exception in self.EXCEPTIONS
            ):  # pragma: no cover
                return

            assert not resource.name.endswith(
                "s"
            ), f"Table {resource} seems to be plural. All tables should be singular."


class ResourceNameIsNotSqlKeyword(GuidelineTesterVisitor):
    """Ensures that all resources have a name that is not a keyword."""

    # List from extracted from https://www.w3schools.com/sql/sql_ref_keywords.asp
    SQL_KEY_WORDS = [
        "add",
        "all",
        "alter",
        "and",
        "any",
        "as",
        "asc",
        "avg",
        "backup",
        "between",
        "by",
        "case",
        "check",
        "column",
        "constraint",
        "count",
        "create",
        "database",
        "default",
        "delete",
        "desc",
        "distinct",
        "drop",
        "exec",
        "exists",
        "foreign",
        "from",
        "full",
        "group",
        "having",
        "in",
        "index",
        "inner",
        "insert",
        "into",
        "is",
        "join",
        "key",
        "left",
        "like",
        "limit",
        "max,",
        "min,",
        "not",
        "null",
        "or",
        "outer",
        "primary",
        "procedure",
        "replace",
        "right",
        "rownum",
        "select",
        "set",
        "sum,",
        "table",
        "top",
        "truncate",
        "union",
        "unique",
        "update",
        "values",
        "view",
        "where",
    ]

    def visit(self, resource: Table | Column):
        # another test ensures that all resources are snake case
        # thus we don't need to care about casing here. It is safe to assume that
        # all names are lower case.
        assert not any(resource.name == kw for kw in self.SQL_KEY_WORDS), (
            f"{resource.__class__.__name__} {resource} has a SQL keyword as name. "
            "Please choose a different name. Note that the keyword name may be "
            "prefixed or suffixed with some context to make it valid."
        )


class ResourceNameIsNotPythonKeyword(GuidelineTesterVisitor):
    """Ensures that all resources have a name that is not a keyword."""

    # List from extracted from https://www.w3schools.com/python/python_ref_keywords.asp
    PYTHON_KEY_WORDS = [
        "and",
        "as",
        "assert",
        "break",
        "case",
        "class",
        "continue",
        "def",
        "del",
        "elif",
        "else",
        "except",
        "false",
        "finally",
        "for",
        "from",
        "global",
        "if",
        "import",
        "in",
        "is",
        "lambda",
        "none",
        "nonlocal",
        "match",
        "not",
        "or",
        "pass",
        "raise",
        "return",
        "true",
        "try",
        "while",
        "with",
        "yield",
    ]

    def visit(self, resource: Table | Column):
        # another test ensures that all resources are snake case
        # thus we don't need to care about casing here. It is safe to assume that
        # all names are lower case.

        assert not any(resource.name == kw for kw in self.PYTHON_KEY_WORDS), (
            f"{resource.__class__.__name__} {resource} has a python keyword as name. "
            "Please choose a different name. Note that the keyword name may be "
            "prefixed or suffixed with some context to make it valid."
        )


class ResourceNameIsNotDiscouraged(GuidelineTesterVisitor):
    """Ensures that all resources have a name that is discouraged."""

    # all names of python builtins are discouraged
    DISCOURAGED_NAMES = [
        name.lower()
        for name, obj in vars(builtins).items()
        if isinstance(obj, types.BuiltinFunctionType)
    ]
    # some additionally discouraged names
    DISCOURAGED_NAMES += [
        "uuid",
        "integer",
        "string",
    ]

    def visit(self, resource: Table | Column):
        # another test ensures that all resources are snake case
        # thus we don't need to care about casing here. It is safe to assume that
        # all names are lower case.
        # We also don't need to check for keywords here, as this is done in another
        # test.

        assert not any(resource.name == kw for kw in self.DISCOURAGED_NAMES), (
            f"{resource.__class__.__name__} {resource} has a name that is discouraged "
            "by the naming guidelines. Please choose a different name. "
            "Note that the discouraged name may be prefixed or suffixed with "
            "some context to make it valid."
        )


class ResourceNameIsNotAmbiguous(GuidelineTesterVisitor):
    """Ensures that all resources have a name that is not ambiguous."""

    NAME_TO_REASON = {
        "name": (
            "Choose either 'display_name' for names that must NOT be "
            "translated or 'label' for names that may be translated."
        ),
    }

    def visit(self, resource: Table | Column):
        """Checks that the name of the resource is not ambiguous."""

        for name, reason in self.NAME_TO_REASON.items():
            assert not resource.name == name, (
                f"{resource.__class__.__name__} {resource} has a name that is"
                f" ambiguous: {reason}"
            )


class AssociationTablesObeyStructuralRules(GuidelineTesterVisitor):
    """Ensures that all association tables follow the naming convention."""

    def visit(self, resource: Table | Column):  # pragma: no cover
        if isinstance(resource, Table) and resource.name.endswith("_association"):
            col_cnt = len(resource.columns)
            # association tables may have an additional column
            assert col_cnt <= 3, f"Table {resource} has too many columns."
            # no need to test for id, column, as this is already tested by other tests
            self._validate_fk_column(resource.columns[0])
            self._validate_fk_column(resource.columns[1])

    @staticmethod
    def _validate_fk_column(column: Column):  # pragma: no cover
        """Ensures that the association column follows the structural rules."""
        assert (
            column.nullable is False
        ), f"FK column {column} of associations table can not be nullable."
        assert column.foreign_keys, f"Column {column} is not a foreign key."
        assert (
            len(column.foreign_keys) == 1
        ), f"Column {column} has multiple foreign keys."
        assert column.primary_key, f"Column {column} is not part of the primary key."


@pytest.fixture(  # type: ignore
    scope="session",
    params=[
        pytest.param(visitor(), id=visitor.__name__)  # type: ignore
        for visitor in GuidelineTesterVisitor.__subclasses__()
    ],
)
def db_guide_line_tester(request: FixtureRequest) -> ParameterSet:
    """Fixture to create a guideline tester."""
    return request.param
