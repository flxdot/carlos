from carlos.database.device.device_management import CarlosDevice
from pydantic import TypeAdapter
from starlette.status import HTTP_200_OK
from starlette.testclient import TestClient


def test_list_devices_route(client: TestClient):
    """This test ensures that the list devices route works as expected."""
    response = client.get("/devices")
    assert response.status_code == HTTP_200_OK

    devices = TypeAdapter(list[CarlosDevice]).validate_json(response.content)
    assert isinstance(devices, list)
