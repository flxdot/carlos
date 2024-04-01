__all__ = ["get_websocket_endpoint", "get_websocket_token_endpoint"]

_DEVICE_ENDPOINT = "/devices/{device_id}/ws"


def get_websocket_endpoint(device_id: str) -> str:  # pragma: no cover
    """Returns the websocket endpoint for the edge device."""

    return _DEVICE_ENDPOINT.format(device_id=device_id)


def get_websocket_token_endpoint(device_id: str) -> str:  # pragma: no cover
    """Returns the websocket token endpoint for the edge device."""

    return _DEVICE_ENDPOINT.format(device_id=device_id) + "/token"
