"""This module defines an abstract protocol that can be be implemented by either the
server and client to perform the necessary operations."""

__all__ = [
    "EdgeProtocol",
]
from abc import ABC, abstractmethod

from .messages import CarlosMessage


class EdgeProtocol(ABC):
    """An abstract protocol that defines the necessary operations to be implemented
    by the server and client."""

    @abstractmethod
    async def send(self, message: CarlosMessage) -> None:
        """Send data to the other end of the connection."""
        raise NotImplementedError()

    @abstractmethod
    async def receive(self) -> CarlosMessage:
        """Receive data from the other end of the connection."""
        raise NotImplementedError()
