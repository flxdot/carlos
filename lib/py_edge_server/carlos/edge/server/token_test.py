import secrets

import pytest
from jwt import InvalidTokenError

from .token import issue_token, verify_token


def test_token_interop():
    """This function checks if the token module is able to encode and decode
    token as wanted."""

    device_id = secrets.token_urlsafe(6)
    ip_address = "127.0.0.1"

    token = issue_token(device_id=device_id, ip_address=ip_address)

    decoded = verify_token(token=token, device_id=device_id, ip_address=ip_address)

    # Check some required claims
    assert decoded["sub"] == device_id
    assert decoded["aud"] == ip_address

    # Ensure if missmatch in IP raises an error
    with pytest.raises(InvalidTokenError):
        verify_token(token=token, device_id=device_id, ip_address="0.0.0.0")

    # Ensure that a missmatch in device_id raises an error
    with pytest.raises(InvalidTokenError):
        verify_token(token=token, device_id="invalid", ip_address=ip_address)
