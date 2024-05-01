__all__ = ["ServerEdgeCommunicationHandler"]


from carlos.database.connection import get_async_carlos_db_connection
from carlos.database.context import RequestContext
from carlos.database.device import (
    CarlosDeviceDriverCreate,
    CarlosDeviceSignalCreate,
    create_device_driver,
    create_device_signals,
    get_device_drivers,
    get_device_signals,
    set_device_seen,
)
from carlos.edge.interface import (
    CarlosMessage,
    DeviceConfigPayload,
    DeviceId,
    EdgeCommunicationHandler,
    EdgeProtocol,
    MessageType,
)
from carlos.edge.interface.messages import DeviceConfigResponsePayload

from carlos.edge.server.constants import CLIENT_NAME


class ServerEdgeCommunicationHandler(EdgeCommunicationHandler):
    """Special server side implementation of the EdgeCommunicationHandler."""

    def __init__(self, device_id: DeviceId, protocol: EdgeProtocol):
        super().__init__(device_id=device_id, protocol=protocol)

        self.register_handlers(
            {
                MessageType.DEVICE_CONFIG: self.handle_device_config,
            }
        )

    async def handle_message(self, message: CarlosMessage):
        """Handles the incoming message.

        :param message: The incoming message.
        """

        # make sure that each message from the device marks the device as seen
        async with get_async_carlos_db_connection(
            client_name=CLIENT_NAME
        ) as connection:
            await set_device_seen(
                context=RequestContext(connection=connection), device_id=self.device_id
            )

        await super().handle_message(message)

    async def handle_device_config(
        self, protocol: EdgeProtocol, message: CarlosMessage
    ):
        """Handles the DEVICE_CONFIG message.

        :param protocol: The protocol to use for communication.
        :param message: The incoming message.
        """

        payload = DeviceConfigPayload.model_validate(message.payload)

        async with get_async_carlos_db_connection(
            client_name=CLIENT_NAME
        ) as connection:
            context = RequestContext(connection=connection)

            await self._upsert_driver_metadata(context, payload)

            response = await self._build_device_config_response(context)

        await self.send(response)

    async def _upsert_driver_metadata(
        self, context: RequestContext, payload: DeviceConfigPayload
    ):
        """This functions inserts any new drivers and signals into the database."""

        known_drivers = await get_device_drivers(
            context=context, device_id=self.device_id
        )
        known_driver_index = {
            driver.driver_identifier: driver for driver in known_drivers
        }
        for driver in payload.drivers:
            if driver.identifier not in known_driver_index:
                _ = await create_device_driver(
                    context=context,
                    device_id=self.device_id,
                    driver=CarlosDeviceDriverCreate(
                        display_name=driver.identifier,
                        is_visible_on_dashboard=True,
                        driver_identifier=driver.identifier,
                        direction=driver.direction,
                        driver_module=driver.driver_module,
                    ),
                )

            known_signals = await get_device_signals(
                context=context,
                device_id=self.device_id,
                driver_identifier=driver.identifier,
            )
            known_signal_index = {
                signal.signal_identifier: signal for signal in known_signals
            }

            signals = []
            for signal in driver.signals:
                if signal.signal_identifier not in known_signal_index:
                    signals.append(
                        CarlosDeviceSignalCreate(
                            signal_identifier=signal.signal_identifier,
                            display_name=signal.signal_identifier,
                            unit_of_measurement=signal.unit_of_measurement,
                            is_visible_on_dashboard=True,
                        )
                    )
            if signals:
                await create_device_signals(
                    context=context,
                    device_id=self.device_id,
                    driver_identifier=driver.identifier,
                    signals=signals,
                )

    async def _build_device_config_response(
        self, context: RequestContext
    ) -> CarlosMessage:
        """Builds the DEVICE_CONFIG_RESPONSE message."""

        timeseries_index: dict[str, dict[str, int]] = {}
        update_drivers = await get_device_drivers(
            context=context, device_id=self.device_id
        )
        for driver_ in update_drivers:
            updated_signals = await get_device_signals(
                context=context,
                device_id=self.device_id,
                driver_identifier=driver_.driver_identifier,
            )
            for signal_ in updated_signals:
                timeseries_index.setdefault(driver_.driver_identifier, {})[
                    signal_.signal_identifier
                ] = signal_.timeseries_id

        return CarlosMessage(
            message_type=MessageType.DEVICE_CONFIG_RESPONSE,
            payload=DeviceConfigResponsePayload(timeseries_index=timeseries_index),
        )
