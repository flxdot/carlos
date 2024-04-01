from starlette.status import HTTP_200_OK
from starlette.testclient import TestClient


def test_health_route(client: TestClient):
    response = client.get("/health")
    assert response.status_code == HTTP_200_OK
