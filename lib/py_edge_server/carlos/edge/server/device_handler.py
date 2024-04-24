__all__ = ["ServerEdgeCommunicationHandler"]

from carlos.database.connection import get_async_carlos_db_connection
from carlos.database.context import RequestContext
from carlos.database.device import set_device_seen
from carlos.edge.interface import CarlosMessage, EdgeCommunicationHandler

from carlos.edge.server.constants import CLIENT_NAME


class ServerEdgeCommunicationHandler(EdgeCommunicationHandler):
    """Special server side implementation of the EdgeCommunicationHandler."""

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
