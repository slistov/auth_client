from typing import TYPE_CHECKING
from src.auth_client.domain import model, events, commands

from . import unit_of_work 

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