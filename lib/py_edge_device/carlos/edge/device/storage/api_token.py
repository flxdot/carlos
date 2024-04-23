from datetime import datetime, timedelta

from carlos.edge.interface.types import CarlosSchema
from pydantic import Field
from sqlalchemy import Connection, delete, insert, select

from .orm import ApiTokenOrm


class ApiToken(CarlosSchema):

    token: str = Field(..., max_length=4096, description="The API token.")
    valid_until_utc: datetime = Field(
        ..., description="The UTC datetime when the token expires."
    )

    @property
    def is_valid(self) -> bool:
        """Returns True if the token is still valid."""

        # add some slack to the token validity to ensure that the token is not expired
        return self.valid_until_utc > datetime.utcnow() - timedelta(seconds=30)


def read_api_token(connection: Connection) -> ApiToken | None:
    """Fetches the currently stored API token. Returns None if no token is stored."""

    token_data = connection.execute(select(ApiTokenOrm)).one_or_none()
    if token_data is None:
        return None
    return ApiToken.model_validate(token_data)


def write_api_token(connection: Connection, token: ApiToken) -> ApiToken:
    """Writes the API token to the storage."""
    connection.execute(delete(ApiTokenOrm))
    connection.execute(insert(ApiTokenOrm).values(**token.model_dump()))

    return token
