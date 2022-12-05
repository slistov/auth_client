from typing import Any
from .generic import InvalidHTTPException

class GrantError(InvalidHTTPException):
    """Вернуть общее сообщение об ошибке: {error: state_error}
    
    Добавляет фиксированное сообщение об ошибке к переданному описанию description """
    def __init__(self, description: Any = None) -> None:
        detail = {"error": "grant_error"}
        if description:
            detail.update({"description": description})
        super().__init__(detail=detail)


class InvalidGrant(GrantError):
    def __init__(self, description: Any = None) -> None:
        super().__init__(description)

class InactiveGrant(GrantError):
    """Выделить отдельно ситуацию, когда используют неактивный (использованный)  state.
    По бизнес-процессу в этом случае нужно аннулировать авторизацию,
    так как попытка использовать уже использованный state расценивается как атака
    """
    def __init__(self, description: Any = None) -> None:
        super().__init__(description)
