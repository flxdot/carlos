__all__ = ["does_exist"]

from sqlalchemy import (
    BinaryExpression,
    BooleanClauseList,
    ColumnElement,
    TextClause,
    select,
)

from carlos.database.context import RequestContext

SqlFilter = ColumnElement[bool] | BooleanClauseList | BinaryExpression | TextClause
SqlFilters = SqlFilter | list[SqlFilter]


async def does_exist(context: RequestContext, sql_filters: list[SqlFilter]) -> bool:
    """
    Checks if an entry exists for the given sql filter.

    :param context: Qmulus request context.
    :param sql_filters: Filter of the desired entry
    :return: True if entry exists, False otherwise
    """

    return bool(
        (
            await context.connection.execute(select(1).where(*sql_filters).limit(1))
        ).scalar()
    )
