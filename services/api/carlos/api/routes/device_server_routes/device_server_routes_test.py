import pytest
from carlos.edge.interface import get_websocket_endpoint, get_websocket_token_endpoint
from carlos.edge.interface.endpoint import append_token_query
from starlette.status import HTTP_200_OK
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from testing.expectations import DEVICE_ID


def test_get_device_server_token(client: TestClient):
    """Ensures that the token endpoint returns a token in the required format"""

    response = client.get(get_websocket_token_endpoint(DEVICE_ID))

    assert response.status_code == HTTP_200_OK, response.text
    assert (
        "text/plain" in response.headers["content-type"]
    ), "The content type is not text/plain."


def test_get_device_server_websocket_connection(client: TestClient):
    """This test ensures that the websocket connection can be established."""

    response = client.get(get_websocket_token_endpoint(DEVICE_ID))

    if response.status_code != HTTP_200_OK:
        pytest.skip(
            "The token endpoint did not return a token, check: "
            "`test_get_device_server_token`"
        )
    token = response.text

    base_ws_uri = get_websocket_endpoint(DEVICE_ID)
    with client.websocket_connect(
        append_token_query(base_ws_uri, token=token)
    ) as websocket:
        # we can not test if the protocol works, as the test client does not support
        # async operations
        assert websocket

    # Invalid token will cause the connection to be closed
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            append_token_query(base_ws_uri, token="invalid_token")
        ) as websocket:
            # we can not test if the protocol works, as the test client does not support
            # async operations
            assert websocket
