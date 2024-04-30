"""This module defines the available commands between the Carlos backend and the
Carlos Edge device."""

__all__ = [
    "CarlosMessage",
    "CarlosPayload",
    "DeviceConfigPayload",
    "DeviceConfigResponsePayload",
    "DriverDataPayload",
    "DriverTimeseries",
    "EdgeVersionPayload",
    "MessageType",
    "PingMessage",
    "PongMessage",
]

import secrets
import string
from abc import ABC
from enum import Enum

from pydantic import Field, ValidationError, model_validator

from carlos.edge.interface.device.driver_config import DriverMetadata
from carlos.edge.interface.types import CarlosSchema


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

    DEVICE_CONFIG = "device_config"
    """Send by the client after successfully connecting to the server.
    This message contains the device config. It is used by the server to create the
    required data structures to store the devices data and to know which data can be
    received from and by the device."""

    DEVICE_CONFIG_RESPONSE = "device_config_response"
    """Send by the server as a response to a DEVICE_CONFIG message. This message 
    contains the timeseries ids for each driver and signal."""

    DRIVER_DATA = "driver_data"
    """Send by the device. This message contains a collection of samples measured 
    by the device."""

    DRIVER_DATA_ACK = "driver_data_ack"
    """Send by the server. This message is a response to a DRIVER_DATA message."""


class CarlosPayloadBase(CarlosSchema, ABC):
    """Common base class for all payload classes."""


MESSAGE_SEPERATOR = "|"

CarlosPayload = CarlosPayloadBase | None


class CarlosMessage(CarlosSchema):
    """Defines the payload of a Carlos message."""

    message_type: MessageType = Field(
        ...,
        description="The type of the message.",
    )

    payload: CarlosPayload = Field(
        ...,
        description="The payload of the message.",
    )

    @property
    def payload_model(self) -> type[CarlosPayloadBase] | None:
        """Returns the model for the payload of this message."""

        # we have a test, that ensures, that all message types have a model
        return MESSAGE_TYPE_TO_MODEL[self.message_type]

    @model_validator(mode="after")
    def validate_message_type_matches_payload(self):
        """Ensure that the message type matches the payload type."""

        # we have a test, that ensures, that all message types have a model
        expected_model = self.payload_model

        if expected_model is None:
            if self.payload is not None:
                raise ValueError(
                    f"Message type {self.message_type.value} does not support "
                    f"a payload. Please set payload to None."
                )
            return self

        assert self.payload is not None, "Payload must not be None"

        if not isinstance(self.payload, expected_model):
            raise ValueError(
                f"Payload type ({self.payload.__class__.__name__}) does not match "
                f"expected model for payload {expected_model.__name__}."
            )

        return self

    def build(self) -> str:
        """Builds the message as a string. This is used by the transport layer
        to send messages over the wire."""

        if self.payload is None:
            return self.message_type.value

        return (
            self.message_type.value
            + MESSAGE_SEPERATOR
            + self.payload.model_dump_json(indent=0, by_alias=True)
        )

    @classmethod
    def from_str(cls, payload: str) -> "CarlosMessage":
        """Parses a CarlosMessage from a string. This is used by the transport layer
        to receive messages from the wire."""

        message_type_str, *payloads = payload.split(MESSAGE_SEPERATOR, 1)

        try:
            message_type = MessageType(message_type_str)
        except ValueError:
            raise ValueError(f"Unsupported message type: {message_type_str}")

        model = MESSAGE_TYPE_TO_MODEL[message_type]

        if model is None:
            return cls(message_type=message_type, payload=None)

        payload = payloads[0]
        if not payload:
            raise ValueError(f"Missing payload for message type {message_type}.")

        try:
            return cls(
                message_type=message_type,
                payload=model.model_validate_json(payload),
            )
        except ValidationError as e:
            raise ValueError(f"Invalid payload for message type {message_type}.") from e


PingMessage = None
PongMessage = None


class EdgeVersionPayload(CarlosPayloadBase):
    """Defines the payload of a EDGE_VERSION message."""

    version: str = Field(
        # we choose as short a possible alias to save bandwidth
        ...,
        alias="v",
        description="The version of the Carlos Edge device.",
    )


SID_SIZE = 6


def generate_staging_id() -> str:
    """Staging ids are used to allow confirmation of successful data transmission."""

    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(SID_SIZE)
    )


class DriverTimeseries(CarlosPayloadBase):
    """Defines the payload of a EDGE_VERSION message."""

    timestamps_utc: list[int] = Field(
        # we choose as short a possible alias to save bandwidth
        ...,
        alias="ts",
        description="A list of timestamps in UTC when the data was recorded.",
    )

    values: list[float] = Field(
        # we choose as short a possible alias to save bandwidth
        ...,
        alias="v",
        description="A list of values for the respective signal.",
    )


class DriverDataPayload(CarlosPayloadBase):
    """Defines the payload of a DRIVER_DATA message."""

    staging_id: str = Field(
        # we choose as short a possible alias to save bandwidth
        default_factory=generate_staging_id,
        alias="sid",
        max_length=SID_SIZE,
        description="The staging id of the Carlos Edge device.",
    )

    data: dict[int, DriverTimeseries] = Field(
        # we choose as short a possible alias to save bandwidth
        ...,
        alias="d",
        description="A mapping of the timeseries_id on the server to the actual"
        "timeseries data.",
    )


class DriverDataAckPayload(CarlosPayloadBase):
    """Defines the payload of a DRIVER_DATA_ACK message."""

    staging_id: str = Field(
        # we choose as short a possible alias to save bandwidth
        ...,
        alias="sid",
        max_length=SID_SIZE,
        description="The staging id of the Carlos Edge device.",
    )


class DeviceConfigPayload(CarlosPayloadBase):
    """Send by the client after successfully connecting to the server.
    This message contains the device config. It is used by the server to create the
    required data structures to store the devices data and to know which data can be
    received from and by the device."""

    drivers: list[DriverMetadata] = Field(
        ...,
        description="The driver configuration for the device.",
    )


class DeviceConfigResponsePayload(CarlosPayloadBase):
    """Send by the server as a response to a DEVICE_CONFIG message. This message
    contains the timeseries ids for each driver and signal."""

    timeseries_index: dict[str, dict[str, int]] = Field(
        ...,
        description="A mapping of the driver identifier to a mapping of the signal "
        "identifier to the timeseries id.",
    )


MESSAGE_TYPE_TO_MODEL: dict[MessageType, type[CarlosPayloadBase] | None] = {
    MessageType.PING: PingMessage,
    MessageType.PONG: PongMessage,
    MessageType.EDGE_VERSION: EdgeVersionPayload,
    MessageType.DEVICE_CONFIG: DeviceConfigPayload,
    MessageType.DEVICE_CONFIG_RESPONSE: DeviceConfigResponsePayload,
    MessageType.DRIVER_DATA: DriverDataPayload,
    MessageType.DRIVER_DATA_ACK: DriverDataAckPayload,
}
