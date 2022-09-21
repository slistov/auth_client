from typing import TYPE_CHECKING, Any
from src.auth_client.domain import model, events, commands
from src.auth_client import config

from . import unit_of_work 

from fastapi.exceptions import HTTPException
from fastapi import status


class InvalidHTTPException(HTTPException):
    def __init__(self, detail: Any) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class InvalidState(InvalidHTTPException):
    def __init__(self, description: Any = None) -> None:
        detail = {"error": "state_error"}
        if description:
            detail.update({"description": description})
        super().__init__(detail=detail)


def create_state(
    cmd: commands.CreateState,
    uow: unit_of_work.AbstractUnitOfWork
) -> str:
    with uow:
        state = model.State()
        uow.states.add(state)
        uow.commit()
        return state.code


def validate_state(
    cmd: commands.ValidateState,
    uow: unit_of_work.AbstractUnitOfWork
) -> bool:
    with uow:
        state = uow.states.get(cmd.code)
        if state is None:
            raise InvalidState("State not found")
        if not state.is_active:
            raise InvalidState("State is inactive")
        uow.commit()
        return state


def state_expired(
    event: events.StateExpired,
    uow: unit_of_work.AbstractUnitOfWork
):
    pass


def auth_code_recieved(
    event: events.AuthCodeRecieved,
    uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        state = uow.states.get(event.state_code)
        if state is None or not state.is_active:
            raise InvalidState()
        state.deactivate()
        grant = uow.grants.add("authorization_code", event.auth_code)
        uow.commit()


