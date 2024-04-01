__all__ = ["DEVICE_CONNECTION_MANAGER"]

from carlos.edge.server.connection import DeviceConnectionManager

DEVICE_CONNECTION_MANAGER = DeviceConnectionManager()
"""Singleton instance of the DeviceConnectionManager."""
