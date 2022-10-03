# pylint: disable=no-self-use
from datetime import date
from unittest import mock
import pytest
from auth_client.adapters import repository
from auth_client.domain import commands, events
from auth_client.service_layer import handlers, messagebus, unit_of_work

from auth_client.domain import model

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
    def test_authorization_is_created_and_could_be_found_by_stateCode(self):
        """Содать авторизацию
        После создания авторизации, её можно получить по state-коду"""
        uow = FakeUnitOfWork()
        messagebus.handle(commands.CreateAuthorization("test_state_code"), uow)
        assert uow.authorizations.get_by_state_code("test_state_code") is not None
        assert uow.committed
    
    def test_state_becomes_inactive_after_AuthCodeGrant_processed(self):
        """Деактивировать state после получения кода авторизации
        Сервис авторизации отдаёт нам код авторизации и прилагает код state.
        Код state необходимо деактивировать"""
        uow = FakeUnitOfWork()
        results = messagebus.handle(commands.CreateAuthorization("test_state_code"), uow)
        auth = results.pop(0)
        messagebus.handle(commands.ProcessGrantRecieved(auth.state.code,  "authorization_code", "test_code"), uow)
        auth = uow.authorizations.get_by_grant_code("test_code")
        assert not auth.state.is_active
    

class TestProcessGrantRecieved_AuthCode:
    """Обработать полученный код авторизации
    
    С кодом авторизации приходит state - в зависимости от его валидации
    либо принимаем код авторизации, либо отвергаем операцию"""
    def test_for_existing_authorization_by_grant(self):
        uow = FakeUnitOfWork()
        results = messagebus.handle(commands.CreateAuthorization("test_state_code"), uow)
        auth = results.pop(0)
        messagebus.handle(commands.ProcessGrantRecieved(auth.state.code,  "authorization_code", "test_code"), uow)
        assert uow.authorizations.get_by_grant_code("test_code") is not None
        assert uow.committed

    def test_for_existing_authorization_wrong_stateCode_raises_InvalidState_exception(self):
        uow = FakeUnitOfWork()
        results = messagebus.handle(commands.CreateAuthorization("test_state_code"), uow)
        auth = results.pop(0)

        with pytest.raises(handlers.InvalidState, match="No active authorization found"):
            messagebus.handle(commands.ProcessGrantRecieved("wrong_state_code", "authorization_code", "test_code"), uow)

    def test_for_existing_authorization_inactive_stateCode_raises_INACTIVEState_exception(self):
        uow = FakeUnitOfWork()
        results = messagebus.handle(commands.CreateAuthorization("test_state_code"), uow)
        auth = results.pop(0)
        auth.state.deactivate()

        with pytest.raises(handlers.InactiveState, match="State is inactive"):
            messagebus.handle(commands.ProcessGrantRecieved("test_state_code", "authorization_code", "test_code"), uow)


class Test_Process_AccessToken_Recieved:
    def test_for_existing_authorization_by_access_token(self):
        uow = FakeUnitOfWork()
        history = [
            commands.CreateAuthorization("test_state_code"),
            commands.ProcessGrantRecieved("test_state_code", "authorization_code", "test_code"),
        ]
        for message in history:
            messagebus.handle(message, uow)
        auth = uow.authorizations.get_by_grant_code("test_code")
        auth.tokens.append(model.Token("test_token"))

        assert uow.authorizations.get_by_token("test_token") is not None
        assert uow.committed


class TestAttackHandling:
    def test_for_existing_authorization_inactive_STATECode_deactivates_authorization_completely(self):
        uow = FakeUnitOfWork()
        results = messagebus.handle(commands.CreateAuthorization("test_state_code"), uow)
        auth = results.pop(0)

        grant = model.Grant("authorization_code", "test_code")
        auth.grants.append(grant)

        token = model.Token(access_token="test_token", expires_in=3600)
        auth.tokens.append(token)

        assert auth.is_active == True
        assert auth.state.is_active 
        assert grant.is_active
        assert token.is_active

        auth.state.deactivate()
        with pytest.raises(handlers.InactiveState, match="State is inactive"):
            messagebus.handle(commands.ProcessGrantRecieved("test_state_code", "authorization_code", "test_code"), uow)

        assert not auth.is_active
        assert not auth.state.is_active 
        assert not grant.is_active
        assert not token.is_active

