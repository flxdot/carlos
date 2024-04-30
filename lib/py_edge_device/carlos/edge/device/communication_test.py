from random import randint
from uuid import uuid4

from carlos.edge.interface import CarlosMessage, MessageType
from carlos.edge.interface.messages import DeviceConfigResponsePayload
from carlos.edge.interface.plugin_pytest import EdgeProtocolTestingConnection
from sqlalchemy.ext.asyncio import AsyncConnection

from carlos.edge.device.communication import (
    ClientEdgeCommunicationHandler,
    handle_device_config_response,
)
from carlos.edge.device.storage.connection import build_storage_url
from carlos.edge.device.storage.timeseries_index import (
    TimeseriesIndex,
    find_timeseries_index,
)
from conftest import TEST_STORAGE_PATH


class TestDeviceCommunicationHandler:

    def test_init(
        self,
        edge_testing_protocol: tuple[
            EdgeProtocolTestingConnection, EdgeProtocolTestingConnection
        ],
    ):
        """This test simply ensures that the ClientEdgeCommunicationHandler can be created.

        Since we have no other logic in the ClientEdgeCommunicationHandler at the moment
        it makes no sense to rest more already tested functionality.
        """

        assert ClientEdgeCommunicationHandler(
            protocol=edge_testing_protocol[0], device_id=uuid4()
        )


async def test_handle_device_config_response(
    edge_testing_protocol: tuple[
        EdgeProtocolTestingConnection, EdgeProtocolTestingConnection
    ],
    temporary_timeseries_index: TimeseriesIndex,
    async_connection: AsyncConnection,
):

    async_engine_url = build_storage_url(TEST_STORAGE_PATH, is_async=True)

    server_timeseries_id = randint(0, 100)

    message = CarlosMessage(
        message_type=MessageType.DEVICE_CONFIG_RESPONSE,
        payload=DeviceConfigResponsePayload(
            timeseries_index={
                temporary_timeseries_index.driver_identifier: {
                    temporary_timeseries_index.driver_signal: server_timeseries_id,
                }
            }
        ),
    )

    await handle_device_config_response(
        protocol=edge_testing_protocol[0],
        message=message,
        url=async_engine_url,
    )

    index = await find_timeseries_index(
        connection=async_connection,
        driver_identifier=temporary_timeseries_index.driver_identifier,
        driver_signal=temporary_timeseries_index.driver_signal,
    )

    assert len(index) == 1, (
        "There should be exactly one entry in the timeseries index"
        "for the given parameters"
    )

    assert (
        index[0].server_timeseries_id == server_timeseries_id
    ), "The server_timeseries_id should be updated"
