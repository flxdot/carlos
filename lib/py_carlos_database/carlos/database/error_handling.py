__all__ = ["PostgresErrorCodes", "is_postgres_error_code"]

from enum import Enum

from sqlalchemy.exc import DBAPIError


class PostgresErrorCodes(str, Enum):  # pragma: no cover
    """A list of handled postgres error codes.

    The full list is available at:
    https://www.postgresql.org/docs/current/errcodes-appendix.html
    """

    NOT_NULL_VIOLATION = "23502"
    FOREIGN_KEY_VIOLATION = "23503"
    UNIQUE_VIOLATION = "23505"
    CHECK_VIOLATION = "23514"

    DUPLICATE_TABLE = "42P07"


def is_postgres_error_code(
    error: DBAPIError, error_code: PostgresErrorCodes
) -> bool:  # pragma: no cover
    """Checks if the error code is a postgres error code.

    :param error: The integrity error returned by sqlalchemy
    :param error_code: The error code to check
    """
    return bool(
        error.orig and hasattr(error.orig, "pgcode") and error.orig.pgcode == error_code
    )
