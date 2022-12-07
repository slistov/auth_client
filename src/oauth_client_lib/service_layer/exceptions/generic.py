from typing import Any
from fastapi import status
from fastapi.exceptions import HTTPException

class InvalidHTTPException(HTTPException):
    """Вернуть статус 403"""
    def __init__(self, detail: Any) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
