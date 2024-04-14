"""The token module contains the code to issue and verify authentication tokens for
the edge protocol."""

__all__ = [
    "issue_token",
    "verify_token",
]

import secrets
from datetime import UTC, datetime, timedelta

import jwt
from carlos.edge.interface import DeviceId

TOKEN_BITS = 2048

KEY = secrets.token_urlsafe(32)
# todo: replace with actual URL of API
ISSUER = __package__


def issue_token(device_id: DeviceId, hostname: str):
    """Issues a new token.

    :param device_id: Used as the subject of the token. It is to prevent that other
        devices can use the token.
    :param hostname: Used as the audience of the token. It is to prevent that other
        devices can use the token.
    :returns: The issued token.
    """

    now = datetime.now(tz=UTC)

    return jwt.encode(
        {
            "iat": now,
            "iss": ISSUER,
            "exp": now + timedelta(minutes=1),
            "sub": str(device_id),
            "aud": hostname,
        },
        key=KEY,
        algorithm="HS256",
    )


def verify_token(token: str, device_id: DeviceId, hostname: str):
    """Verifies a token.

    :param token: The token to verify.
    :param device_id: Is checked against the subject claim.
    :param hostname: Is checked against the audience claim.
    :raises InvalidTokenError: If the token is invalid.
    """

    decoded = jwt.decode(
        token,
        key=KEY,
        algorithms=["HS256"],
        audience=hostname,
        issuer=ISSUER,
        options={
            "require": ["aud", "sub", "exp", "iss"],
            "verify_exp": True,
        },
    )

    if decoded["sub"] != str(device_id):
        raise jwt.InvalidTokenError("The device ID does not match the token.")

    return decoded
