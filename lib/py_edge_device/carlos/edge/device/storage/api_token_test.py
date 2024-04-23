import secrets
from datetime import datetime, timedelta

from sqlalchemy import Connection

from .api_token import ApiToken, read_api_token, write_api_token


def test_api_token_is_valid():
    token = ApiToken(
        token="test_token",
        valid_until_utc=datetime.utcnow() + timedelta(seconds=30),
    )

    assert token.is_valid, "Token should be valid"

    token = ApiToken(
        token="test_token",
        valid_until_utc=datetime.utcnow() - timedelta(seconds=30),
    )
    assert not token.is_valid, "Token should be invalid"


def test_api_token(sync_connection: Connection):

    no_token = read_api_token(connection=sync_connection)
    assert no_token is None, "No token should be present in the database."

    new_token = ApiToken(
        token=secrets.token_hex(1024),
        valid_until_utc=datetime.utcnow() + timedelta(days=1),
    )

    write_api_token(connection=sync_connection, token=new_token)

    stored_token = read_api_token(connection=sync_connection)
    assert stored_token == new_token, "Stored token should match the written token."

    # check if overwriting works
    newer_token = ApiToken(
        token=secrets.token_hex(1024),
        valid_until_utc=datetime.utcnow() + timedelta(days=1),
    )
    write_api_token(connection=sync_connection, token=newer_token)
    stored_token = read_api_token(connection=sync_connection)
    assert stored_token == newer_token, "Stored token should match the written token."
