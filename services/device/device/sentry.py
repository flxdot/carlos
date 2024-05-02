from pathlib import Path

import sentry_sdk
import yaml
from loguru import logger
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


class SentrySettings(BaseSettings):  # pragma: no cover

    SENTRY_DSN: str = Field(
        ...,
        description="The DSN tells the SDK where to send the events. If this value "
        "is not provided, the SDK will try to read it from the "
        "SENTRY_DSN environment variable. If that variable also does not exist, "
        "the SDK will just not send any events.",
    )


def setup_sentry():  # pragma: no cover

    try:
        with open(Path.cwd() / "sentry_config", "r") as file:
            sentry_config = SentrySettings.model_validate(yaml.safe_load(file))
    except FileNotFoundError:
        return
    except ValidationError:
        logger.exception("Failed to validate sentry config.")

    sentry_sdk.init(
        dsn=sentry_config.SENTRY_DSN,
        integrations=[
            AsyncioIntegration(),
            HttpxIntegration(),
            SqlalchemyIntegration(),
            LoguruIntegration(),
        ],
    )
