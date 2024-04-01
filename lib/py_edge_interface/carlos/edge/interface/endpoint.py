__all__ = [
    "append_token_query",
    "get_websocket_endpoint",
    "get_websocket_token_endpoint",
]

from urllib import parse as urlparse
from urllib.parse import urlencode

_DEVICE_ENDPOINT = "/devices/{device_id}/ws"


def get_websocket_endpoint(device_id: str) -> str:  # pragma: no cover
    """Returns the websocket endpoint for the edge device."""

    return _DEVICE_ENDPOINT.format(device_id=device_id)


def get_websocket_token_endpoint(device_id: str) -> str:  # pragma: no cover
    """Returns the websocket token endpoint for the edge device."""

    return _DEVICE_ENDPOINT.format(device_id=device_id) + "/token"


def append_token_query(uri: str, token: str) -> str:  # pragma: no cover
    """Appends the token to the URI."""

    url_parts = list(urlparse.urlparse(uri))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update({"token": token})
    url_parts[4] = urlencode(query)
    return str(urlparse.urlunparse(url_parts))
