__all__ = ["RequestContext"]

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncConnection


@dataclass(frozen=True, slots=True)
class RequestContext:
    connection: AsyncConnection
