from carlos.database.data.timeseries import TimeseriesData
from carlos.database.device import CarlosDeviceSignal
from pydantic import TypeAdapter
from starlette.testclient import TestClient


async def test_get_timeseries_route(
    client: TestClient,
    driver_signals: list[CarlosDeviceSignal],
):
    """Test the get_timeseries_route."""

    response = client.get(
        "/data/timeseries",
        params={
            "timeseriesId": [signal.timeseries_id for signal in driver_signals],
            "start_at_utc": "2022-01-01T00:00:00Z",
            "end_at_utc": "2022-01-02T00:00:00Z",
        },
    )
    assert response.status_code == 200

    data = TypeAdapter(list[TimeseriesData]).validate_json(response.content)

    assert len(data) == 2
