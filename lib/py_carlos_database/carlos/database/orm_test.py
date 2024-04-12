"""This module contains test to enforce common design guidelines of the
tables/ORM models.

To implement new tests for the design guidelines, add a new object to this module.
Make sure to inherit from the `DesignGuidelineTest` class and implement the visit()
method. The visit() method will be called for each table and column in the database.

We test the ORM models against the guidelines and the reflected tables are compared
against ORM models. This eliminates the need to test the reflected tables against the
naming guidelines. The respective test that did that have been removed.
"""

from typing import Collection, Iterable

import pytest
from _pytest.fixtures import FixtureRequest
from sqlalchemy import Column, MetaData, Table, text
from sqlalchemy.engine import Connection
from sqlalchemy.sql.elements import TextClause

from .orm import ALL_SCHEMA_NAMES, CarlosModelBase
from .plugin_pytest import GuidelineTesterVisitor, new_engine

# Holds the list of defines ORM models. We store this here, to prevent an overwrite
# by the schema reflection fixture further down.
REGISTERED_ORM_MODELS = CarlosModelBase.metadata.sorted_tables


@pytest.fixture(
    scope="session",
    params=[pytest.param(table, id=table.fullname) for table in REGISTERED_ORM_MODELS],
)
def data_model_table(request: FixtureRequest) -> Table:
    """Fixture to provide a table from the data model."""
    return request.param


def test_enforce_design_guidelines_tables(
    data_model_table: Table, db_guide_line_tester: GuidelineTesterVisitor
):
    """Ensures that the design guidelines are followed."""
    db_guide_line_tester.visit(data_model_table)


@pytest.mark.parametrize(
    "orm_model",
    [pytest.param(orm(), id=orm.__name__) for orm in CarlosModelBase.__subclasses__()],
)
def test_orm_models_have_orm_suffix(
    orm_model: CarlosModelBase,
):
    """Ensures that all orm models have the suffix Orm in the class name."""
    assert orm_model.__class__.__name__.endswith(
        "Orm"
    ), f"Orm model {orm_model.__class__.__name__} does not end with Orm."


@pytest.mark.parametrize(
    "column",
    [
        pytest.param(column, id=f"{column.table.fullname}.{column.name}")
        for table in REGISTERED_ORM_MODELS
        for column in table.columns
    ],
)
def test_enforce_design_guidelines_columns(
    column: Column, db_guide_line_tester: GuidelineTesterVisitor
):
    """Ensures that the design guidelines are followed.

    We test columns individually instead of during the
    test_enforce_design_guidelines_columns(), to get violations for all columns
    in one test run. Otherwise, we would only get the first violation with each
    test run.

    We did not introduce a fixture for the columns, as they are not reused yet.
    """
    db_guide_line_tester.visit(column)


@pytest.fixture(scope="session")
def carlos_database_tables_reflected() -> list[Table]:
    """Fixture to ensure that all tables are reflected."""

    tables = {}
    with new_engine() as engine:
        for schema in ALL_SCHEMA_NAMES:
            meta = MetaData(schema=schema)
            meta.reflect(bind=engine, views=False)
            # make sure not to include any duplicated tables
            tables.update(
                {
                    str(tab): tab
                    for tab in meta.tables.values()
                    if str(tab) not in tables
                }
            )

        with engine.begin() as conn:
            partition_child_tables = get_partition_child_tables(
                connection=conn, tables=tables.values()
            )

    # remove all partition child tables, as they are not part of the data model
    return [
        t
        for t in tables.values()
        if t.fullname not in partition_child_tables and t.schema in ALL_SCHEMA_NAMES
    ]


def get_partition_child_tables(
    connection: Connection, tables: Iterable[Table]
) -> set[str]:
    """Returns a set of all partition child tables."""
    partition_child_tables = set()
    for table in tables:
        result = connection.execute(
            text(
                f"""
                SELECT inhrelid::regclass AS child
                FROM   pg_catalog.pg_inherits
                WHERE  inhparent = '{table.fullname}'::regclass;
                """
            )
        )
        for full_table_name in result:
            partition_child_tables.add(full_table_name[0])
    return partition_child_tables


def test_reflected_and_orm_are_in_sync(
    carlos_database_tables_reflected: Collection[Table],
):
    """Ensures that the reflected tables and the ORM models are in sync."""

    registered_cnt = len(REGISTERED_ORM_MODELS)
    reflected_cnt = len(carlos_database_tables_reflected)
    assert registered_cnt == reflected_cnt, (
        f"The number of ORM models ({registered_cnt}) "
        f"and the number of reflected tables ({reflected_cnt}) are not equal. "
        "Please update the ORM models accordingly or introduce a new migration."
    )


class TestOrmModelsInSyncWithReflectedTables:
    """Ensures that the ORM models and the reflected tables are in sync."""

    def test_table_is_in_sync_with_database(
        self,
        carlos_database_tables_reflected: Collection[Table],
        data_model_table: Table,
    ):
        """Ensures that the ORM models and the reflected tables are in sync."""

        reflected_table_index = {
            table.fullname: table for table in carlos_database_tables_reflected
        }

        try:
            reflected = reflected_table_index[data_model_table.fullname]
        except KeyError:
            pytest.fail(
                f"Table {data_model_table} is not reflected or has a different name."
            )

        # check the relevant table properties
        assert (
            data_model_table.comment == reflected.comment
        ), "The comments are not equal."
        assert len(data_model_table.columns) == len(
            reflected.columns
        ), "The number of columns is not equal."

        reflected_column_index = {column.name: column for column in reflected.columns}

        for registered_column in data_model_table.columns:
            try:
                reflected_column = reflected_column_index[registered_column.name]
            except KeyError:
                pytest.fail(
                    f"Column {registered_column} is not reflected or has a different "
                    "name."
                )

            self._ensure_columns_equal(
                registered_column=registered_column, reflected_column=reflected_column
            )

    @staticmethod
    def _ensure_columns_equal(registered_column: Column, reflected_column: Column):
        full_column_name = (
            f"{registered_column.table.fullname}.{registered_column.name}"
        )

        assert registered_column.primary_key == reflected_column.primary_key, (
            f"The primary key attribute of {full_column_name} is not equal: "
            f"{registered_column.primary_key} != {reflected_column.primary_key}"
        )
        # We need to compare the types as strings, as the types are not equal
        assert str(registered_column.type) == str(reflected_column.type), (
            f"The type of {full_column_name} is not equal: "
            f"{registered_column.type} != {reflected_column.type}"
        )
        assert registered_column.comment == reflected_column.comment, (
            f"The comments of {full_column_name} are not equal: "
            f"'{registered_column.comment}' != '{reflected_column.comment}'"
        )
        assert registered_column.nullable == reflected_column.nullable, (
            f"The nullability of {full_column_name} is not equal: "
            f"{registered_column.nullable} != {reflected_column.nullable}"
        )

        # This condition may NOT be simplified
        if registered_column.autoincrement is not True:
            assert registered_column.default == reflected_column.default, (
                f"The default of {full_column_name} is not equal: "
                f"{registered_column.default} != {reflected_column.default}"
            )
            ensure_server_default_is_equal(
                full_column_name=full_column_name,
                reflected_column=reflected_column,
                registered_column=registered_column,
            )

        # check the foreign keys
        ensure_fk_are_equal(
            full_column_name=full_column_name,
            reflected_column=reflected_column,
            registered_column=registered_column,
        )


def ensure_server_default_is_equal(
    full_column_name: str, reflected_column: Column, registered_column: Column
):
    reflected_default = reflected_column.server_default
    registered_default = registered_column.server_default

    if reflected_default is None and registered_default is None:
        return

    assert isinstance(registered_default, type(reflected_default)), (
        f"{full_column_name} has different default types: "
        f"{type(registered_default)} != {type(reflected_default)}"
    )
    assert registered_default.arg.text == reflected_default.arg.text
    if isinstance(registered_default.arg, TextClause):
        assert registered_default.arg.text == reflected_default.arg.text, (
            f"{full_column_name} has different default values: "
            f"{registered_default.arg.text} != {reflected_default.arg.text}"
        )
    else:
        # If you see this test fail, it could either be that your migration or ORM is
        # wrong or that the test is missing a special case as above. If later is the
        # case, I have some bad news for you: You need to add the special case to the
        # test.
        assert registered_default.arg == reflected_default.arg, (
            f"{full_column_name} has different default values: "
            f"{registered_default.arg} != {reflected_default.arg}"
        )


def ensure_fk_are_equal(
    full_column_name: str, reflected_column: Column, registered_column: Column
):
    """Ensures that the foreign keys are equal."""

    registered_fk_cnt = len(registered_column.foreign_keys)
    if registered_fk_cnt == 0:
        return

    assert (
        registered_fk_cnt <= 1
    ), "There should not be more then one foreign key constraint."
    assert registered_fk_cnt == len(
        reflected_column.foreign_keys
    ), "The number of foreign keys is not equal."

    registered_fk = list(registered_column.foreign_keys)[0]
    reflected_fk = list(reflected_column.foreign_keys)[0]

    assert registered_fk.column.name == reflected_fk.column.name, (
        f"The foreign key columns of {full_column_name} are not equal: "
        f"{registered_fk.column.name} != {reflected_fk.column.name}"
    )
    assert registered_fk.ondelete == reflected_fk.ondelete, (
        f"The ondelete clause of the FK {full_column_name} is not equal: "
        f"{registered_fk.ondelete} != {reflected_fk.ondelete}"
    )
    assert registered_fk.onupdate == reflected_fk.onupdate, (
        f"The on update clause of the FK {full_column_name} is not equal: "
        f"{registered_fk.onupdate} != {reflected_fk.onupdate}"
    )
