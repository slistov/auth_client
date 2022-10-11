"""Обработчики команд и событий

Команды и события генерируются в точках входа, см. /entrypoints
"""

from typing import TYPE_CHECKING, Any
from auth_client.domain import model, events, commands
from auth_client import config

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


def create_authorization(
    cmd: commands.CreateAuthorization,
    uow: unit_of_work.AbstractUnitOfWork
) -> model.Authorization:
    with uow:
        state = model.State()
        auth = model.Authorization(state=state)
        uow.authorizations.add(auth)
        uow.commit()
        return auth


def process_grant_recieved(
    cmd: commands.ProcessGrantRecieved,
    uow: unit_of_work.AbstractUnitOfWork
):
    """Обработчик команды Обработать код авторизации
    """
    with uow:
        auth = uow.authorizations.get_by_state_code(cmd.state_code)        
        if auth is None or not auth.is_active:
            raise InvalidState("No active authorization found")

        if cmd.type == "authorization_code" and cmd.state_code:            
            if not auth.state.is_active:                        # Exception: are we under attack?
                auth.deactivate()                               # if we are, then invoke authorization
                uow.commit()
                raise InactiveState("State is inactive")
            auth.state.deactivate()

        grant = model.Grant(cmd.type, cmd.code)
        auth.grants.append(grant)
        uow.commit()


def request_token(
    cmd: commands.RequestToken,
    uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        auth = uow.authorizations.get_by_grant_code(cmd.grant_code)
        if auth is None or not auth.is_active:
            raise InvalidGrant("No active authorization found")
        
        old_grant = auth.get_grant_by_code(cmd.grant_code)
        if not old_grant or not old_grant.is_active:
            raise InvalidGrant("No grant found for token requesting")
        old_grant.deactivate()

        old_token = auth.get_active_token()
        if old_token:
            old_token.deactivate()

        token_requester = uow.get_token_requester()
        data = token_requester.prepare_tokenRequest_data(old_grant)
        token_requester.post("/token", data)

        new_token = token_requester.get_token()
        new_grant = token_requester.get_grant()
        auth.tokens.append(new_token)
        auth.grants.append(new_grant)        
        uow.commit()
        