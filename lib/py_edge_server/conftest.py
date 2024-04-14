import pytest
from devtools.context_manager import EnvironmentContext


@pytest.fixture(scope="session", autouse=True)
def api_test_environment(carlos_db_test_environment):

    with EnvironmentContext(environment_variables={}, echo=None):
        yield
