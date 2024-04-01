__all__ = ["CarlosAPISettings"]

import logging

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings


class CarlosAPISettings(BaseSettings):
    """Defines the settings that can be altered for the Carlos API."""

    LOG_LEVEL: int = Field(
        logging.INFO,
        description=(
            "The logging level for the application, the log level is on an "
            "integer scale, see "
            "https://docs.python.org/3/library/logging.html#levels for details. "
            "Passing the level names is also accepted."
        ),
    )

    @field_validator("LOG_LEVEL", mode="before")
    def _validate_log_level(cls, v):
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            log_level_int = logging.getLevelName(v)
            if log_level_int is not None:
                return log_level_int
        raise ValueError(
            "Log level needs to be a valid `logging` log level. Either as int or str."
            f"Got: {v} of type {v.__class__.__name__}."
        )

    API_DOCS_ENABLED: bool = Field(
        False,
        description=(
            "If True, the SwaggerUI and openapi.json is accessible "
            "without authentication"
        ),
    )
    API_DEACTIVATE_USER_AUTH: bool = Field(
        False,
        description=(
            "If True, the user authentication is deactivated. "
            "This is useful for testing purposes."
        ),
    )

    API_CORS_ORIGINS: list[AnyHttpUrl] = Field(
        default_factory=list,
        description=(
            "A JSON-formatted list of origins. For example: "
            '["http://localhost", "http://localhost:4200", '
            '"http://localhost:3000", "http://localhost:8080"]'
        ),
    )
