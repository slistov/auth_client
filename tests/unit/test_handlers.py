# pylint: disable=no-self-use
from datetime import date
from unittest import mock
import pytest
from src.auth_client.adapters import repository
from src.auth_client.domain import commands, events
from src.auth_client.service_layer import handlers, messagebus, unit_of_work

from src.auth_client.domain import model

class FakeRepository(repository.AbstractRepository):
    def __init__(self, authorizations):
        super().__init__()
        self._authorizations = set(authorizations)

    def _add(self, authorization):
        self._authorizations.add(authorization)

    def _get_by_state_code(self, code) -> model.Authorization:
        return next(
            (a for a in self._authorizations if code == a.state.code), None
        )

    def _get_by_grant_code(self, code):
        return next(
            (a for a in self._authorizations for grant in a.grants if code == grant.code), None
        )

    def _get_by_token(self, access_token) -> model.Authorization:
        return next(
            (a for a in self._authorizations for token in a.tokens if access_token == token.access_token), None
        )


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.authorizations = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


class TestAuthorization:
    def test_auth_creation(self):
        uow = FakeUnitOfWork()
        messagebus.handle(commands.CreateAuthorization("test_state_code"), uow)
        assert uow.authorizations.get_by_state_code("test_state_code") is not None
        assert uow.committed
    

class TestAuthorizationCodeRecieving:
    def test_for_existing_authorization_by_grant(self):
        uow = FakeUnitOfWork()
        results = messagebus.handle(commands.CreateAuthorization("test_state_code"), uow)
        auth = results.pop(0)
        messagebus.handle(commands.ProcessAuthCodeRecieved(state_code=auth.state.code, auth_code="test_code"), uow)
        assert uow.authorizations.get_by_grant_code("test_code") is not None
        assert uow.committed


    def test_for_existing_authorization_wrong_stateCode_raises_InvalidState_exception(self):
        uow = FakeUnitOfWork()
        results = messagebus.handle(commands.CreateAuthorization("test_state_code"), uow)
        auth = results.pop(0)

        with pytest.raises(handlers.InvalidState, match="No active authorization found"):
            messagebus.handle(commands.ProcessAuthCodeRecieved("wrong_state_code", "test_code"), uow)

    def test_for_existing_authorization_inactive_stateCode_raises_INACTIVEState_exception(self):
        uow = FakeUnitOfWork()
        results = messagebus.handle(commands.CreateAuthorization("test_state_code"), uow)
        auth = results.pop(0)
        auth.state.deactivate()

        with pytest.raises(handlers.InactiveState, match="State is inactive"):
            messagebus.handle(commands.ProcessAuthCodeRecieved("test_state_code", "test_code"), uow)

    def test_for_existing_authorization_inactive_stateCode_deactivates_authorization_and_its_grants_and_tokens(self):
        uow = FakeUnitOfWork()
        results = messagebus.handle(commands.CreateAuthorization("test_state_code"), uow)
        auth = results.pop(0)
        auth.state.deactivate()

        with pytest.raises(handlers.InactiveState, match="State is inactive"):
            messagebus.handle(commands.ProcessAuthCodeRecieved("test_state_code", "test_code"), uow)
        
        assert auth.is_active == False
        assert auth.state.is_active == False


class TestAccessTokenRecieving:
    def test_for_existing_authorization_by_access_token(self):
        uow = FakeUnitOfWork()
        results = messagebus.handle(commands.CreateAuthorization("test_state_code"), uow)
        auth = results.pop(0)
        results = messagebus.handle(commands.ProcessAuthCodeRecieved("test_state_code", "test_grant_code"), uow)
        messagebus.handle(events.TokenRecieved("test_grant_code", "test_token"), uow)
        assert uow.authorizations.get_by_token("test_token") is not None
        assert uow.committed
