"""Обработчики команд и событий

Команды и события генерируются в точках входа, см. /entrypoints
"""

from typing import TYPE_CHECKING, Any
from src.auth_client.domain import model, events, commands
from src.auth_client import config

from . import unit_of_work 

from fastapi.exceptions import HTTPException
from fastapi import status


class InvalidHTTPException(HTTPException):
    """Вернуть статус 403"""
    def __init__(self, detail: Any) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class StateError(InvalidHTTPException):
    """Вернуть общее сообщение об ошибке: {error: state_error}
    
    Добавляет фиксированное сообщение об ошибке к переданному описанию description """
    def __init__(self, description: Any = None) -> None:
        detail = {"error": "state_error"}
        if description:
            detail.update({"description": description})
        super().__init__(detail=detail)


class InvalidState(StateError):
    def __init__(self, description: Any = None) -> None:
        super().__init__(description)

class InactiveState(StateError):
    """Выделить отдельно ситуацию, когда используют неактивный (использованный)  state.
    По бизнес-процессу в этом случае нужно аннулировать авторизацию,
    так как попытка использовать уже использованный state расценивается как атака
    """
    def __init__(self, description: Any = None) -> None:
        super().__init__(description)


def create_authorization(
    cmd: commands.CreateAuthorization,
    uow: unit_of_work.AbstractUnitOfWork
) -> model.Authorization:
    with uow:
        state = model.State(code=cmd.state_code)
        auth = model.Authorization(state=state)
        uow.authorizations.add(auth)
        uow.commit()
        return auth


# def grant_recieved(
#     event: events.GrantRecieved,
#     uow: unit_of_work.AbstractUnitOfWork
# ):
#     """Обработчик события Получен грант
#     """
#     with uow:
#         auth = uow.authorizations.get_by__code(event.state_code)
#         if auth is None or not auth.is_active or not auth.state.is_active:
#             raise InvalidState()
#         auth.state.deactivate()
#         auth.grants.append("authorization_code", event.auth_code)
#         uow.commit()


def process_auth_code_recieved(
    cmd: commands.ProcessAuthCodeRecieved,
    uow: unit_of_work.AbstractUnitOfWork
):
    """Обработчик команды Обработать код авторизации
    """
    with uow:
        auth = uow.authorizations.get_by_state_code(cmd.state_code)
        if auth is None or not auth.is_active:
            raise InvalidState("No active authorization found")
        
        if not auth.state.is_active:
            raise InactiveState("State is inactive")

        auth.state.deactivate()
        grant = model.Grant("authorization_code", cmd.auth_code)
        auth.grants.append(grant)
        uow.commit()


def token_recieved(
    event: events.TokenRecieved,
    uow: unit_of_work.AbstractUnitOfWork
):
        auth = uow.authorizations.get_by_grant_code(event.grant_code)
        grant = auth.get_grant_by_code(event.grant_code)
        if auth is None or not auth.is_active or not grant.is_active:
            raise InvalidState()
        grant.deactivate()
        token = model.Token("test_token")
        auth.tokens.append(token)
        uow.commit()
