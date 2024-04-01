"""This module is based on the example provided in the Auth0 documentation for FastAPI:

https://auth0.com/blog/build-and-secure-fastapi-server-with-auth0/
"""

__all__ = ["VerifyToken", "cached_token_verify_from_env"]

import os
import secrets
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from carlos.api.config import CarlosAPISettings


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):  # pragma: no cover
        """Returns HTTP 403"""
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    def __init__(self):  # pragma: no cover
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
    def domain(self) -> str:  # pragma: no cover
        """Returns the Auth0 domain based on the region."""
        return f"{self.tenant_id}.{self.region.value}.auth0.com"

    @property
    def issuer(self) -> str:  # pragma: no cover
        """Returns the issuer URL for the Auth0 tenant."""
        return f"https://{self.domain}/"


# A random token that is used for testing only. Since this token changes every
# time the server is restarted and has a decent length
# (possible combinations for 2^2048 bits = 3.23e616), we can assume that this
# "backdoor" isn't too dangerous.
TESTING_TOKEN = secrets.token_urlsafe(256)

TESTING_TOKEN_DATA = {
    "sub": "offline",
    "iss": "https://test",
    "aud": "pytest",
    "iat": datetime.now().timestamp(),
    "exp": (datetime.now() + timedelta(minutes=30)).timestamp(),
}


class VerifyToken:
    """Does all the token verification using PyJWT"""

    def __init__(self, config: Auth0Settings):
        self.config = config

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f"https://{self.config.domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    async def verify(
        self,
        security_scopes: SecurityScopes,
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    ) -> dict:  # pragma: no cover
        """Verifies the token and returns the payload if it is valid."""

        if token is None:
            # If the flag is set to deactivate the user authentication, then
            # return a deactivated user
            if CarlosAPISettings().API_DEACTIVATE_USER_AUTH:
                return TESTING_TOKEN_DATA
            raise UnauthenticatedException()

        # special backdoor for testing. Impact on security should be too bad. 🤞
        if token.credentials == TESTING_TOKEN and os.getenv("ENVIRONMENT") == "pytest":
            return TESTING_TOKEN_DATA

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
                algorithms=[self.config.algorithm],
                audience=self.config.audience,
                issuer=self.config.issuer,
            )
        except Exception as error:
            raise UnauthorizedException(str(error))

        return payload


@lru_cache()
def cached_token_verify_from_env():
    """A cached dependency to construct the VerifyToken object.

    This is useful to avoid reading the environment variables too often.
    It further prevents that the environment variables are read during import.
    """
    return VerifyToken(config=Auth0Settings()).verify
