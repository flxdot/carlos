from carlos.database.device import CarlosDeviceSignal, CarlosDeviceSignalUpdate
from carlos.edge.interface.units import UnitOfMeasurement
from starlette.testclient import TestClient


def test_update_device_signal_route(
    client: TestClient, driver_signals: list[CarlosDeviceSignal]
):

    to_update = CarlosDeviceSignalUpdate(
        display_name="Temperature Fahrenheit",
        unit_of_measurement=UnitOfMeasurement.FAHRENHEIT,
        is_visible_on_dashboard=False,
    )

    response = client.put(
        f"/signals/{driver_signals[0].timeseries_id}",
        json=to_update.dict(),
    )
    assert response.is_success, response.text
    updated = CarlosDeviceSignal.model_validate(response.json())

    assert updated.display_name == to_update.display_name
    assert updated.unit_of_measurement == to_update.unit_of_measurement
    assert updated.is_visible_on_dashboard == to_update.is_visible_on_dashboard
