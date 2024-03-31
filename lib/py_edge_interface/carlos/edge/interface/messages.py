"""This module defines the available commands between the Carlos backend and the
Carlos Edge device."""

__all__ = [
    "CarlosMessage",
    "EdgeVersionMessage",
    "MessageType",
    "PingMessage",
    "PongMessage",
    "build_payload",
    "parse_payload",
]

from abc import ABC
from enum import Enum
from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class MessageType(str, Enum):
    """Defines the possible messages that can be exchanged between the Carlos backend
    and the Carlos Edge device."""

    PING = "ping"
    """Requests the communication partner to respond with a PONG command. This is 
    used to check if the communication partner is still available."""

    PONG = "pong"
    """The communication partner sends this command as a response to a PING command."""

    EDGE_VERSION = "edge_version"
    """Requests the communication partner to respond with the version of the Carlos Edge
    device. This is used to determine if a Carlos Edge device requires an update."""


class CarlosMessageBase(BaseModel, ABC):
    """Common base class for all message payloads exchanged between the Carlos backend
    and the Carlos Edge device."""

    model_config = ConfigDict(
        # Whether an aliased field may be populated by its name as given by the model
        # attribute, as well as the alias.
        populate_by_name=True,
        # Whether to build models and look up discriminators of tagged unions using
        # python object attributes.
        from_attributes=True,
        # We always want to strip whitespace from strings, as this is usually
        # a potential source of errors.
        str_strip_whitespace=True,
    )


CarlosMessage = TypeVar("CarlosMessage", CarlosMessageBase, None)

PingMessage = None
PongMessage = None


class EdgeVersionMessage(CarlosMessageBase):
    """Defines the payload of a EDGE_VERSION message."""

    version: str = Field(
        # we choose as short a possible alias to save bandwidth
        ...,
        alias="v",
        description="The version of the Carlos Edge device.",
    )


_MESSAGE_TYPE_TO_MODEL: dict[MessageType, type[CarlosMessageBase] | None] = {
    MessageType.PING: PingMessage,
    MessageType.PONG: PongMessage,
    MessageType.EDGE_VERSION: EdgeVersionMessage,
}

MESSAGE_SEPERATOR = "|"


def build_payload(message_type: MessageType, message: CarlosMessage) -> str:
    """Builds a CarlosMessage from a payload dictionary.

    :param message_type: the message type
    :param message: the payload dictionary
    :return: the message as a string
    :raises ValueError: If the type of the message and the message type do not match
    """

    expected_model = _MESSAGE_TYPE_TO_MODEL[message_type]
    if expected_model is None:
        if message is not None:
            raise ValueError(
                f"Message type {message_type} does not match message {message}"
            )
        return message_type.value + MESSAGE_SEPERATOR

    if not isinstance(message, expected_model):
        raise ValueError(
            f"Message type {message_type} does not match message {message}"
        )

    return MESSAGE_SEPERATOR.join(
        (message_type.value, message.model_dump_json(indent=0, by_alias=True))
    )


def parse_payload(payload: str) -> tuple[MessageType, CarlosMessage]:
    """Parses a CarlosMessage from a string.

    :param payload: the message as a string
    :return: the payload dictionary
    :raises ValueError: if the message payload is not supported
    """

    message_type_str, message_payload = payload.split(MESSAGE_SEPERATOR, 1)

    try:
        message_type = MessageType(message_type_str)
    except ValueError:
        raise ValueError(f"Unsupported message type: {message_type_str}")

    model = _MESSAGE_TYPE_TO_MODEL[message_type]

    if model is None:
        return message_type, None  # type: ignore
    try:
        return message_type, model.model_validate_json(message_payload)  # type: ignore
    except ValidationError:
        raise ValueError(
            f"Invalid payload for message type {message_type}: {message_payload}"
        )
