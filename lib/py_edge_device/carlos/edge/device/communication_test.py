from uuid import uuid4

from carlos.edge.interface.plugin_pytest import EdgeProtocolTestingConnection

from carlos.edge.device.communication import DeviceCommunicationHandler


class TestDeviceCommunicationHandler:

    def test_init(
        self,
        edge_testing_protocol: tuple[
            EdgeProtocolTestingConnection, EdgeProtocolTestingConnection
        ],
    ):
        """This test simply ensures that the DeviceCommunicationHandler can be created.

        Since we have no other logic in the DeviceCommunicationHandler at the moment
        it makes no sense to rest more already tested functionality.
        """

        assert DeviceCommunicationHandler(
            protocol=edge_testing_protocol[0], device_id=uuid4()
        )
