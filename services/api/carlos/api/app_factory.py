__all__ = ["create_app"]

from typing import Any

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from pydantic.alias_generators import to_camel
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.asyncpg import AsyncPGIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from .config import CarlosAPISettings
from .logging_patch import setup_logging

DOCS_URL = "/docs"
OPENAPI_URL = "/openapi.json"


def create_app(api_settings: CarlosAPISettings | None = None) -> FastAPI:
    """Creates and configures the FastAPI app."""

    from .routes import main_router, public_router

    api_settings = api_settings or CarlosAPISettings()

    configure_sentry()

    # ensures that the logging is handled via loguru
    setup_logging(level=api_settings.LOG_LEVEL)

    app = FastAPI(
        title="Carlos API",
        # todo: find a way to get the version from the package in the Dockerfile
        version="0.1.0",  # version(__package__),
        docs_url=DOCS_URL if api_settings.API_DOCS_ENABLED else None,
        openapi_url=OPENAPI_URL if api_settings.API_DOCS_ENABLED else None,
        generate_unique_id_function=_generate_openapi_operation_id,
    )

    setup_middlewares(app=app, api_settings=api_settings)

    app.include_router(main_router)
    app.include_router(public_router)

    return app


def _generate_openapi_operation_id(route: APIRoute) -> str:
    """Generates a simpler version of the OpenAPI operation ids.
    They are used as method names for generated clients."""
    return to_camel(route.name)


def setup_middlewares(
    app: FastAPI,
    api_settings: CarlosAPISettings,
) -> None:
    """Sets the application middlewares. For more details about middleware check
    https://fastapi.tiangolo.com/tutorial/middleware/.

    :param app: an application instance
    :param api_settings: the application settings
    """

    app.add_middleware(CORSMiddleware, **get_cors_kwargs(api_settings))
    app.add_middleware(GZipMiddleware)


def get_cors_kwargs(api_settings: CarlosAPISettings) -> dict[str, Any]:
    """Returns the kwargs required to configure the CORS middleware."""
    return {
        "allow_origins": [
            # Pydantics AnyUrl will add `/` to the end of each URL
            # But the origins must not have a trailing slash
            str(origin).rstrip("/")
            for origin in api_settings.API_CORS_ORIGINS
        ],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }


def configure_sentry():
    sentry_sdk.init(
        integrations=[
            AsyncPGIntegration(),
            AsyncioIntegration(),
            FastApiIntegration(),
            HttpxIntegration(),
            LoguruIntegration(),
            SqlalchemyIntegration(),
        ],
    )
