import pytest

from carlos.edge.interface.messages import (
    MESSAGE_TYPE_TO_MODEL,
    CarlosMessage,
    CarlosPayload,
    CarlosSchema,
    EdgeVersionPayload,
    MessageType,
)


@pytest.mark.parametrize("message_type", list(MessageType))
def test_all_message_types_have_model(message_type: MessageType):
    """This test ensures that all message types have a corresponding model."""

    assert message_type in MESSAGE_TYPE_TO_MODEL, f"Missing model for {message_type}"


class NonUsedPayload(CarlosSchema):
    """A payload that is not used in the message types."""

    some_attr: str


class TestCarlosMessage:
    """This test class tests the CarlosMessage class."""

    @pytest.mark.parametrize(
        "message_type, payload",
        [
            pytest.param(
                MessageType.PING,
                EdgeVersionPayload(version="1.0.0"),
                id="Wrong payload for payloadless message",
            ),
            pytest.param(MessageType.EDGE_VERSION, None, id="Missing payload"),
            pytest.param(
                MessageType.EDGE_VERSION,
                NonUsedPayload(some_attr="1.1.0"),
                id="wrong payload model",
            ),
        ],
    )
    def test_model_validator(self, message_type: MessageType, payload: CarlosPayload):
        """This test ensures that the build_payload function raises a ValueError for
        invalid payloads."""

        with pytest.raises(ValueError):
            CarlosMessage(message_type=message_type, payload=payload)

    @pytest.mark.parametrize(
        "message_type, payload",
        [
            pytest.param(MessageType.PING, None, id="message without payload"),
            pytest.param(
                MessageType.EDGE_VERSION,
                EdgeVersionPayload(version="1.0.0"),
                id="message with payload",
            ),
        ],
    )
    def test_payload_conversion(
        self, message_type: MessageType, payload: CarlosMessage
    ):
        """This test ensures that the conversion function are compatible."""

        transport_layer_payload = CarlosMessage(
            message_type=message_type, payload=payload
        ).build()

        parsed = CarlosMessage.from_str(transport_layer_payload)
        assert (
            message_type == parsed.message_type
        ), f"Expected {message_type}, got {parsed.message_type}"
        assert payload == parsed.payload, f"Expected {payload}, got {parsed.payload}"

    @pytest.mark.parametrize(
        "transport_layer_payload",
        [
            pytest.param("INVALID|", id="invalid message type"),
            pytest.param(MessageType.EDGE_VERSION.value + "|", id="missing payload"),
            pytest.param(
                MessageType.EDGE_VERSION.value + '|{"some_attr": "2.3.1"}',
                id="wrong format",
            ),
        ],
    )
    def test_from_str(self, transport_layer_payload: str):
        """This test ensures that the parse_payload function raises a ValueError for
        invalid payloads."""

        with pytest.raises(ValueError):
            CarlosMessage.from_str(transport_layer_payload)
