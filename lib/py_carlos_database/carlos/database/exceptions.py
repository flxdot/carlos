from fastapi import HTTPException
from starlette import status


class NotFound(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """Returns HTTP 403"""
        super().__init__(status.HTTP_404_NOT_FOUND, detail=detail)
