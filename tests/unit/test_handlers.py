# pylint: disable=no-self-use
from datetime import date
from unittest import mock
import pytest
from src.auth_client.adapters import repository
from src.auth_client.domain import commands, events
from src.auth_client.service_layer import handlers, messagebus, unit_of_work

from src.auth_client.domain import model

class FakeRepository(repository.AbstractRepository):
    def __init__(self, states):
        super().__init__()
        self._states = set(states)

    def _add(self, state):
        self._states.add(state)

    def _get(self, code):
        return next((p for p in self._states if p.code == code), None)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.states = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


class TestState:
    def test_create_state(self):
        uow = FakeUnitOfWork()
        results = messagebus.handle(commands.CreateState(), uow)
        state_code = results.pop(0)

        db_state = uow.states.get(state_code)
        assert db_state.code == state_code
        assert uow.committed
    
    def test_validate_state_valid(self):
        uow = FakeUnitOfWork()
        state = model.State()
        uow.states.add(state)

        results = messagebus.handle(commands.ValidateState(code="test_code"), uow)
        assert results.pop(0)

    def test_validate_state_wrong_stateCode(self):
        uow = FakeUnitOfWork()
        state = model.State()
        uow.states.add(state)

        with pytest.raises(handlers.InvalidState, match="State not found"):
            messagebus.handle(commands.ValidateState("any_wrong_state"), uow)

    def test_validate_state_inactive(self):
        uow = FakeUnitOfWork()
        state = model.State()
        state.deactivate()
        uow.states.add(state)

        with pytest.raises(handlers.InvalidState, match="State is inactive"):
            messagebus.handle(commands.ValidateState(state.code), uow)


class TestAuthCode:
    def Test_code():
        pass