from typing import Any
from .generic import InvalidHTTPException


class OAuthError(InvalidHTTPException):
    """Вернуть общее сообщение об ошибке: {error: oauth_error}

    Добавляет фиксированное сообщение об ошибке
    к переданному описанию description"""
    def __init__(self, description: Any = None) -> None:
        detail = {"error": "oauth_error"}
        if description:
            detail.update({"description": description})
        super().__init__(detail=detail)
