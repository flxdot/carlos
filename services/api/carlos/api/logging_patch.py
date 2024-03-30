"""Configure handlers and formats for application loggers."""

import logging
import sys
from pprint import pformat
from typing import Iterable

# if you don't like imports of private modules
# you can move it to typing.py module
from loguru import logger
from loguru._defaults import LOGURU_FORMAT


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See
    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.
    Example:
    """

    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string


LOGGERS_TO_INTERCEPT = (
    "alembic",
    "fastapi",
    "gunicorn",
    "sqlalchemy",
    "uvicorn",
    "uvicorn.access",
)


def setup_logging(level: int = logging.INFO, logger_to_intercept: Iterable[str] = None):
    """
    Replaces logging handlers with a handler for using the custom handler."""

    if logger_to_intercept is None:
        logger_to_intercept = LOGGERS_TO_INTERCEPT

    for logger_name in logger_to_intercept:
        replace_logger(logger_name)

    # set logs output, level and format
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": level,
                "format": format_record,
            }
        ]
    )


def replace_logger(logger_name: str):
    """Replaces a logger from standard lib with a loguru logger."""

    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith(f"{logger_name}.")
    )
    for lib_logger in loggers:
        lib_logger.handlers = []

    # change handler for default uvicorn logger
    intercept_handler = InterceptHandler()
    logging.getLogger(logger_name).handlers = [intercept_handler]
