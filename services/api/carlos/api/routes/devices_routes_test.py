from uuid import uuid4

from carlos.database.device.device_management import (
    CarlosDevice,
    CarlosDeviceCreate,
    CarlosDeviceUpdate,
)
from pydantic import TypeAdapter
from starlette import status
from starlette.testclient import TestClient


def test_list_devices_route(client: TestClient):
    """This test ensures that the list devices route works as expected."""
    response = client.get("/devices")
    assert response.status_code == status.HTTP_200_OK

    devices = TypeAdapter(list[CarlosDevice]).validate_json(response.content)
    assert isinstance(devices, list)


def test_devices_crud(client: TestClient):
    """This test ensures that the devices CRUD routes work as expected."""

    # query non existent device
    device_id = uuid4()
    response = client.get(f"/devices/{device_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text

    # create a new device
    device = CarlosDeviceCreate(display_name="test_device")
    response = client.post("/devices", content=device.model_dump_json())
    assert response.status_code == status.HTTP_200_OK, response.text
    created_device = CarlosDevice.model_validate_json(response.content)
    assert created_device.display_name == device.display_name

    # query the created device
    response = client.get(f"/devices/{created_device.device_id}")
    assert response.status_code == status.HTTP_200_OK, response.text
    queried_device = CarlosDevice.model_validate_json(response.content)
    assert queried_device == created_device

    # update the created device
    updated_device = CarlosDeviceUpdate(
        display_name="updated_device", description="updated"
    )
    response = client.put(
        f"/devices/{created_device.device_id}", content=updated_device.model_dump_json()
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    updated_device = CarlosDevice.model_validate_json(response.content)
    assert updated_device.display_name == "updated_device"
    assert updated_device.description == "updated"
