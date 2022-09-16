from typing import TYPE_CHECKING
from src.auth_client.domain import model, events, commands

from . import unit_of_work 

from fastapi.exceptions import HTTPException


class InvalidState(HTTPException):
    pass


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
        uow.commit()
        return state is not None


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


