import pytest
from devtools.context_manager import EnvironmentContext
from starlette.testclient import TestClient

from carlos.api.app_factory import create_app
from carlos.api.depends.authentication import TESTING_TOKEN, Auth0Region


@pytest.fixture(scope="session", autouse=True)
def api_test_environment(carlos_db_test_environment):

    env = {
        "API_CORS_ORIGINS": '["http://127.0.0.1:8000"]',
        # For development, we want to enable the API docs
        "API_DOCS_ENABLED": "1",
        "API_DEACTIVATE_USER_AUTH": "1",
        # Auth0 Config - Does not matter for testing
        "AUTH0_TENANT_ID": "auth0-tenant-id",
        "AUTH0_REGION": Auth0Region.EUROPE.value,
        "AUTH0_AUDIENCE": "auth0-audience",
        # special undocumented environment variables to deactivate special
        # testing features
        "ENVIRONMENT": "pytest",
    }

    with EnvironmentContext(environment_variables=env, echo=None):
        yield


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Returns a test client that can be used to make requests to the API."""

    return TestClient(
        create_app(), headers={"Authorization": f"Bearer {TESTING_TOKEN}"}
    )
