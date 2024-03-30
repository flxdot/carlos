"""This module is based on the example provided in the Auth0 documentation for FastAPI:

https://auth0.com/blog/build-and-secure-fastapi-server-with-auth0/
"""

__all__ = ["VerifyToken"]

from enum import Enum

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """Returns HTTP 403"""
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication"
        )


class Auth0Region(str, Enum):
    """A list of available regions for Auth0."""

    US = "us"
    EUROPE = "eu"
    AUSTRALIA = "au"
    JAPAN = "jp"


class Auth0Algorithm(str, Enum):
    """A list of available algorithms for Auth0."""

    RS256 = "RS256"
    HS256 = "HS256"


class Auth0Settings(BaseSettings):
    """Configuration settings for Auth0."""

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="AUTH0_", extra="ignore"
    )

    tenant_id: str = Field(..., description="The identifier of the Auth0 tenant.")
    region: Auth0Region = Field(
        Auth0Region.EUROPE, description="The region where the Auth0 tenant is located."
    )
    audience: str = Field(..., description="The audience of the Auth0 API.")
    algorithm: Auth0Algorithm = Field(
        Auth0Algorithm.RS256,
        description="Algorithm to sign the tokens with. When selecting RS256 the token "
        "will be signed with Auth0's private key.",
    )

    @property
    def domain(self) -> str:
        """Returns the Auth0 domain based on the region."""
        return f"{self.tenant_id}.{self.region.value}.auth0.com"

    @property
    def issuer(self) -> str:
        """Returns the issuer URL for the Auth0 tenant."""
        return f"https://{self.domain}/"


class VerifyToken:
    """Does all the token verification using PyJWT"""

    def __init__(self):
        self.config = Auth0Settings()

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f"https://{self.config.domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    async def verify(
        self,
        security_scopes: SecurityScopes,
        token: HTTPAuthorizationCredentials | None = Depends(HTTPBearer()),
    ):
        if token is None:
            raise UnauthenticatedException

        # This gets the 'kid' from the passed token
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(
                token.credentials
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            raise UnauthorizedException(str(error))
        except jwt.exceptions.DecodeError as error:
            raise UnauthorizedException(str(error))

        try:
            payload = jwt.decode(
                token.credentials,
                signing_key,
                algorithms=self.config.auth0_algorithm,
                audience=self.config.auth0_api_audience,
                issuer=self.config.auth0_issuer,
            )
        except Exception as error:
            raise UnauthorizedException(str(error))

        return payload
