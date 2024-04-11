"""This module contains container object that are used to define connection
attributes for our SQL Databases."""

from pydantic import SecretStr
from pydantic.fields import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

DRIVER_NAME = "postgresql+psycopg2"
ASYNC_DRIVER_NAME = "postgresql+asyncpg"


class DatabaseConnectionSettings(BaseSettings):
    """Class for declaring env config variables with type and default values"""

    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    # Details of the connection
    host: str = Field(..., description="Hostname of the DB")
    port: int = Field(5432, description="Port of the DB")
    name: str = Field(
        ...,
        description="Name of the database ",
    )
    user: str = Field(
        ...,
        description="The username used to authenticate against the DB.",
    )
    password: SecretStr = Field(
        ...,
        description="The password used to authenticate against the DB.",
    )

    def __hash__(self) -> int:
        """Used to use this as key in a dict or lru_cache()"""
        return hash(self.url)

    @property
    def url(self) -> URL:  # noqa: F821
        """Returns an instance of sqlalchemy.engine.URL"""

        return URL.create(
            drivername=DRIVER_NAME,
            host=self.host,
            port=self.port,
            database=self.name,
            username=self.user,
            password=self.password.get_secret_value(),
        )

    @property
    def async_url(self) -> URL:  # noqa: F821
        """Returns an instance of sqlalchemy.engine.URL with async pgdb drivername"""

        return URL.create(
            drivername=ASYNC_DRIVER_NAME,
            host=self.host,
            port=self.port,
            database=self.name,
            username=self.user,
            password=self.password.get_secret_value(),
        )


class EngineSettings(BaseSettings):
    """Holds the setting of an SQL Alchemy Engine."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Optional Connection parameters
    SQA_ENGINE_POOL_SIZE: int = Field(
        10,
        description=(
            "The number of connections to keep open inside the "
            "connection pool. A pool_size setting of 0 indicates no limit."
        ),
    )
    SQA_ENGINE_MAX_OVERFLOW: int = Field(
        20,
        description=(
            "The number of connections to allow in connection pool "
            "'overflow', that is connections that can be opened above and beyond "
            "the pool_size setting, which defaults to five."
        ),
    )
    SQA_ENGINE_POOL_TIMEOUT: int = Field(
        10,
        description=(
            "Number of seconds to wait before giving up on getting a "
            "connection from the pool. This can be a float but is subject to the "
            "limitations of Python time functions which may not be reliable in the "
            "tens of milliseconds."
        ),
    )
    SQA_ENGINE_CONNECTION_TIMEOUT: int = Field(
        2,
        description=(
            "Number of seconds to wait before giving up on establishing a new "
            "connection"
        ),
    )
    DEBUG: bool = Field(
        False,
        description="If activated all SQL queries are printed to `std.out`.",
    )
