import pytest

from carlos.edge.interface.messages import (
    _MESSAGE_TYPE_TO_MODEL,
    CarlosMessage,
    EdgeVersionMessage,
    MessageType,
    build_payload,
    parse_payload,
)


@pytest.mark.parametrize("message_type", list(MessageType))
def test_all_message_types_have_model(message_type: MessageType):
    """This test ensures that all message types have a corresponding model."""

    assert message_type in _MESSAGE_TYPE_TO_MODEL, f"Missing model for {message_type}"


@pytest.mark.parametrize(
    "message_type, message",
    [
        pytest.param(MessageType.PING, None, id="message without payload"),
        pytest.param(
            MessageType.EDGE_VERSION,
            EdgeVersionMessage(version="1.0.0"),
            id="message with payload",
        ),
    ],
)
def test_payload_conversion(message_type: MessageType, message: CarlosMessage):
    """This test ensures that the conversion function are compatible."""

    payload = build_payload(message_type=message_type, message=message)

    parsed_message_type, parsed_message = parse_payload(payload=payload)
    assert (
        message_type == parsed_message_type
    ), f"Expected {message_type}, got {parsed_message_type}"
    assert message == parsed_message, f"Expected {message}, got {parsed_message}"


@pytest.mark.parametrize(
    "message_type, message",
    [
        pytest.param(
            MessageType.PING,
            EdgeVersionMessage(version="1.0.0"),
            id="wrong message type",
        ),
        pytest.param(MessageType.EDGE_VERSION, None, id="wrong message"),
    ],
)
def test_build_payload_raises_value_error(
    message_type: MessageType, message: CarlosMessage
):
    """This test ensures that the build_payload function raises a ValueError for
    invalid payloads."""

    with pytest.raises(ValueError):
        build_payload(message_type=message_type, message=message)


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param("INVALID|", id="invalid message type"),
        pytest.param(
            MessageType.EDGE_VERSION.value + '|{"some_attr": "2.3.1"}',
            id="wrong format",
        ),
    ],
)
def test_parse_payload_raises_value_error(payload: str):
    """This test ensures that the parse_payload function raises a ValueError for
    invalid payloads."""

    with pytest.raises(ValueError):
        parse_payload(payload=payload)
