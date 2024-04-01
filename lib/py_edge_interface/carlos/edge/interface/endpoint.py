
DEVICE_ENDPOINT = "/devices/{device_id}/ws"
"""This is the endpoint that needs the be provided to the edge device to connect to 
the API."""


def get_websocket_endpoint(device_id: str) -> str:
    """Returns the websocket endpoint for the edge device."""

    return DEVICE_ENDPOINT.format(device_id=device_id)


def get_websocket_token_endpoint(device_id: str) -> str:
    """Returns the websocket token endpoint for the edge device."""

    return DEVICE_ENDPOINT.format(device_id=device_id) + "/token"