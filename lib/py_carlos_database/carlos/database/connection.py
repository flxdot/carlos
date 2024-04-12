__all__ = [
    "EngineFactory",
    "OptionalConnectArgs",
    "get_async_carlos_database_engine",
    "get_async_carlos_db_connection",
    "get_carlos_database_engine",
]

import asyncio
import json
from contextlib import asynccontextmanager
from datetime import timedelta
from functools import lru_cache, partial
from typing import Annotated, Any, AsyncIterator, Hashable

from pydantic import BaseModel, BeforeValidator, Field, PlainSerializer
from pydantic_core import to_jsonable_python
from sqlalchemy import NullPool, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from .config import DatabaseConnectionSettings, EngineSettings

_DEFAULT_CLIENT_NAME = "carlos"


def millisecond_validator(v: str | int | timedelta) -> timedelta:  # pragma: no cover
    """Validates that the passed value is a positive integer."""
    if not isinstance(v, (timedelta, int, str)):
        raise ValueError("Value must be a timedelta, int or string.")

    if isinstance(v, str):
        v = int(v)

    if isinstance(v, int):
        v = timedelta(milliseconds=v)

    if v < timedelta(milliseconds=0):
        raise ValueError("Value must be a positive integer.")

    return v


def millisecond_serializer(v: timedelta) -> str:
    """Serializes a timedelta to milliseconds as string."""
    return str(int(v.total_seconds() * 1000))


MilliSecondsTimedelta = Annotated[
    timedelta,
    BeforeValidator(millisecond_validator),
    PlainSerializer(millisecond_serializer),
]


class PostgresClientConnectionDefaults(BaseModel, Hashable):
    """This model contain some of the connection defaults according to:
    https://www.postgresql.org/docs/current/runtime-config-client.html
    """

    statement_timeout: MilliSecondsTimedelta | None = Field(
        None,
        description="""
            Abort any statement that waits longer than the specified amount of time
            while attempting to acquire a lock on a table, index, row, or other
            database object. The time limit applies separately to each lock acquisition
            attempt. The limit applies both to explicit locking requests (such as
            LOCK TABLE, or SELECT FOR UPDATE without NOWAIT) and to implicitly-acquired
            locks. If this value is specified without units, it is taken as
            milliseconds. A value of zero (the default) disables the timeout.

            Unlike statement_timeout, this timeout can only occur while waiting for
            locks. Note that if statement_timeout is nonzero, it is rather pointless
            to set lock_timeout to the same or larger value, since the statement
            timeout would always trigger first. If log_min_error_statement is set to
            ERROR or lower, the statement that timed out will be logged.

            Setting lock_timeout in postgresql.conf is not recommended because it
            would affect all sessions.
        """,
    )
    lock_timeout: MilliSecondsTimedelta | None = Field(
        None,
        description="""
            Abort any statement that takes more than the specified amount of time.
            If log_min_error_statement is set to ERROR or lower, the statement that
            timed out will also be logged. If this value is specified without units,
            it is taken as milliseconds. A value of zero (the default) disables the
            timeout.

            The timeout is measured from the time a command arrives at the server until
            it is completed by the server. If multiple SQL statements appear in a
            single simple-Query message, the timeout is applied to each statement
            separately. (PostgreSQL versions before 13 usually treated the timeout as
            applying to the whole query string.) In extended query protocol, the
            timeout starts running when any query-related message (Parse, Bind,
            Execute, Describe) arrives, and it is canceled by completion of an Execute
            or Sync message.

            Setting statement_timeout in postgresql.conf is not recommended because it
            would affect all sessions.
        """,
    )

    def __hash__(self):
        """Returns the hash of the model."""

        return hash(
            tuple(self.model_dump(exclude_defaults=True, exclude_unset=True).items())
        )

    def __or__(self, other):
        """Returns the union of the two models. If a value is set in both models, the
        value of the other model takes precedence."""
        if other is None:
            return self
        if not isinstance(other, PostgresClientConnectionDefaults):  # pragma: no cover
            return NotImplemented
        return PostgresClientConnectionDefaults(  # pragma: no cover
            **self.model_dump(exclude_defaults=True, exclude_unset=True)
            | other.model_dump(exclude_defaults=True, exclude_unset=True)
        )


# The following options have been introduced to prevent long-running queries and
# locks. The values are in milliseconds. In the past, we had issues with "locked"
# tables, as well as queries that had a huge impact on the performance of the
# database. The values are chosen to be "safe" for the database, but still allow
# for long-running queries for things like the task runner.
DEFAULT_CONNECTION_OPTIONS = PostgresClientConnectionDefaults(
    statement_timeout=timedelta(minutes=10),
    lock_timeout=timedelta(minutes=10),
)


OptionalConnectArgs = PostgresClientConnectionDefaults | None


class EngineFactory:
    """Objects constructs new SQL Alchemy engines based on passed settings."""

    def __init__(
        self,
        client_name: str = "Generic Carlos Python Client",
        connection_settings: DatabaseConnectionSettings | None = None,
        engine_settings: EngineSettings | None = None,
    ):
        """Creates a new EngineBuilder."""
        self.client_name = client_name
        self.connection_settings = connection_settings or DatabaseConnectionSettings()
        self.engine_settings = engine_settings or EngineSettings()

    def _get_engine_kwargs(self, **user_kwargs) -> dict[str, Any]:
        """Returns the shared and default keyword arguments that shall be passed into
        the `create_engine()` and `create_async_engine()` function."""

        kwargs = {
            "echo": self.engine_settings.DEBUG,
            # ensures a connection is alive before it get drawn from the pool
            "pool_pre_ping": True,
        }

        pool_kwargs = {
            "pool_size": self.engine_settings.SQA_ENGINE_POOL_SIZE,
            "max_overflow": self.engine_settings.SQA_ENGINE_MAX_OVERFLOW,
            "pool_timeout": self.engine_settings.SQA_ENGINE_POOL_TIMEOUT,
            "echo_pool": self.engine_settings.DEBUG,
        }
        # The combination of NullPool and the pool_kwargs is not supported
        # by SQLAlchemy
        if (
            "poolclass" in user_kwargs
            and user_kwargs["poolclass"] is not None
            and issubclass(user_kwargs["poolclass"], NullPool)
        ):  # pragma: no cover
            pool_kwargs = {}

        return kwargs | pool_kwargs | user_kwargs

    def new_engine(
        self, connect_args: OptionalConnectArgs = None, **kwargs
    ) -> Engine:  # pragma: no cover
        """
        Builds a new engine with the given settings.

        :param kwargs: Additional keyword arguments passed to sql alchemy's
            `create_engine()`
        :param connect_args: A dictionary of additional connection arguments
            passed to the engine as `connect_args`.
            See:
            https://docs.sqlalchemy.org/en/20/core/engines.html#use-the-connect-args-dictionary-parameter
        :return: Engine
        """

        actual_connection_args = {
            "connect_timeout": self.engine_settings.SQA_ENGINE_POOL_TIMEOUT,
            "application_name": self.client_name,
        }
        if connect_args is not None:
            actual_connection_args["options"] = " ".join(
                [
                    f"-c {key}={value}"
                    for key, value in connect_args.model_dump(
                        exclude_defaults=True, exclude_unset=True
                    ).items()
                ]
            )

        create_engine_kwargs = self._get_engine_kwargs(**kwargs)

        create_engine_kwargs["url"] = self.connection_settings.url
        create_engine_kwargs["connect_args"] = actual_connection_args

        # Create respective connection engine
        return create_engine(**create_engine_kwargs)

    def new_async_engine(
        self, connect_args: OptionalConnectArgs = None, **kwargs
    ) -> AsyncEngine:
        """
        Builds a new async engine with the given settings.

        :param kwargs: Additional keyword arguments passed to sql alchemy's
            `create_async_engine()`
        :param connect_args: A dictionary of additional connection arguments
            passed to the engine as `connect_args`.
            See:
            https://docs.sqlalchemy.org/en/20/core/engines.html#use-the-connect-args-dictionary-parameter
        :return: AsyncEngine
        """

        default_connection_args = {
            # identifies the application in `select * from pg_stat_activity`
            "application_name": self.client_name,
        }
        if connect_args is not None:
            server_settings = default_connection_args | connect_args.model_dump(
                exclude_defaults=True, exclude_unset=True
            )
        else:  # pragma: no cover
            server_settings = default_connection_args

        create_engine_kwargs = self._get_engine_kwargs(**kwargs)

        create_engine_kwargs["url"] = self.connection_settings.async_url
        create_engine_kwargs["connect_args"] = {
            "timeout": self.engine_settings.SQA_ENGINE_POOL_TIMEOUT,
            "server_settings": server_settings,
        }

        # Ensure to always set the async_mode to True
        if "execution_options" in kwargs:  # pragma: no cover
            kwargs["execution_options"]["async_mode"] = True
        else:
            create_engine_kwargs["execution_options"] = {"async_mode": True}

        # Create respective connection engine
        return create_async_engine(**create_engine_kwargs)


@lru_cache(maxsize=2)
def get_carlos_database_engine(
    connection_settings: DatabaseConnectionSettings | None = None,
    client_name: str = _DEFAULT_CLIENT_NAME,
    connection_args: OptionalConnectArgs = None,
) -> Engine:
    """This function returns a sqlalchemy engine for the Carlos Database."""

    engine_factory = EngineFactory(
        client_name=client_name,
        connection_settings=connection_settings or DatabaseConnectionSettings(),
    )
    _db_engine = engine_factory.new_engine(
        connect_args=DEFAULT_CONNECTION_OPTIONS | connection_args
    )

    return _db_engine


@lru_cache(maxsize=2)
def get_async_carlos_database_engine(
    connection_settings: DatabaseConnectionSettings | None = None,
    client_name: str = _DEFAULT_CLIENT_NAME,
    connection_args: OptionalConnectArgs = None,
    **create_engine_kwargs,
) -> AsyncEngine:
    """This function returns a sqlalchemy engine for the Carlos Database."""

    engine_factory = EngineFactory(
        client_name=client_name,
        connection_settings=connection_settings or DatabaseConnectionSettings(),
    )
    _async_db_engine = engine_factory.new_async_engine(
        connect_args=DEFAULT_CONNECTION_OPTIONS | connection_args,
        json_serializer=partial(json.dumps, default=to_jsonable_python),
        **create_engine_kwargs,
    )

    return _async_db_engine


@asynccontextmanager
async def get_async_carlos_db_connection(
    client_name: str = "Carlos Database",
    connection_args: OptionalConnectArgs = None,
) -> AsyncIterator[AsyncConnection]:  # pragma: no cover
    """Returns an async connection for the Carlos Database."""

    async_engine = get_async_carlos_database_engine(
        client_name=f"{client_name} (async - EventLoop {id(asyncio.get_event_loop())})",
        connection_args=connection_args,
    )

    # I'm unsure why the context manager fails at some tests.
    # So we don't use it for now.
    conn = await async_engine.connect()
    try:
        yield conn
        await conn.commit()
    finally:
        await conn.close()
