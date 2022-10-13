# pylint: disable=no-self-use
from datetime import date
from unittest import mock
import pytest
from auth_client.adapters import repository
from auth_client.domain import commands, events
from auth_client.service_layer import handlers, messagebus, unit_of_work, oauth_requester, oauth_service

from auth_client.domain import model
from ..conftest import FakeOAuthService

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

    def _get_token_requester(self):
        return oauth_requester.OAuthRequester(FakeOAuthService("http://fake-oauth.service.com/api"))


class TestAuthorization:
    def test_authorization_is_created_and_could_be_found_by_stateCode(self):
        """Содать авторизацию
        После создания авторизации, её можно получить по state-коду"""
        uow = FakeUnitOfWork()
        [auth] = messagebus.handle(commands.CreateAuthorization("source_url"), uow)
        assert uow.authorizations.get_by_state_code(auth.state.code) is not None
        assert uow.committed
    
    def test_state_becomes_inactive_after_AuthCodeGrant_processed(self):
        """Деактивировать state после получения кода авторизации
        Сервис авторизации отдаёт нам код авторизации и прилагает код state.
        Код state необходимо деактивировать"""
        uow = FakeUnitOfWork()
        [auth] = messagebus.handle(commands.CreateAuthorization("source_url"), uow)
        messagebus.handle(commands.ProcessGrantRecieved(auth.state.code,  "authorization_code", "test_code"), uow)
        assert not auth.state.is_active
    

class TestGrant:
    """Обработать полученный код авторизации
    
    С кодом авторизации приходит state - в зависимости от его валидации
    либо принимаем код авторизации, либо отвергаем операцию"""
    def test_process_grant_recieved_then_get_auth_by_grant_and_get_grant_for_auth(self):
        uow = FakeUnitOfWork()
        [auth] = messagebus.handle(commands.CreateAuthorization("source_url"), uow)
        messagebus.handle(commands.ProcessGrantRecieved(auth.state.code, "authorization_code", "test_code"), uow)
        assert uow.authorizations.get_by_grant_code("test_code") is not None
        assert auth.get_active_grant().code == "test_code"        
        assert uow.committed

    def test_process_grant_with_wrong_stateCode_raises_InvalidState_exception(self):
        uow = FakeUnitOfWork()
        [auth] = messagebus.handle(commands.CreateAuthorization("source_url"), uow)

        with pytest.raises(handlers.InvalidState, match="No active authorization found"):
            messagebus.handle(commands.ProcessGrantRecieved("wrong_state_code", "authorization_code", "test_code"), uow)

    def test_process_grant_with_inactive_stateCode_raises_INACTIVEState_exception(self):
        uow = FakeUnitOfWork()
        [auth] = messagebus.handle(commands.CreateAuthorization("source_url"), uow)
        auth.state.deactivate()

        with pytest.raises(handlers.InactiveState, match="State is inactive"):
            messagebus.handle(commands.ProcessGrantRecieved(auth.state.code, "authorization_code", "test_code"), uow)


class TestAccessToken:
    def test_for_existing_authorization_by_access_token(self):
        uow = FakeUnitOfWork()
        [auth] = messagebus.handle(commands.CreateAuthorization("source_url"), uow)
        messagebus.handle(commands.ProcessGrantRecieved(auth.state.code, "authorization_code", "test_code"), uow)
        auth.tokens.append(model.Token("test_token"))

        assert uow.authorizations.get_by_token("test_token") is not None
        assert uow.committed
    
    def test_get_active_token_for_existing_authorization(self):
        uow = FakeUnitOfWork()
        [auth] = messagebus.handle(commands.CreateAuthorization("source_url"), uow)
        messagebus.handle(commands.ProcessGrantRecieved(auth.state.code, "authorization_code", "test_code"), uow)
        auth.tokens.append(model.Token("test_token"))

        assert auth.get_active_token().access_token == "test_token"
        assert uow.committed


class TestAttackHandling:
    def test_for_existing_authorization_inactive_STATECode_deactivates_authorization_completely(self):
        uow = FakeUnitOfWork()
        [auth] = messagebus.handle(commands.CreateAuthorization("source_url"), uow)
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
            messagebus.handle(commands.ProcessGrantRecieved(auth.state.code, "authorization_code", "test_code"), uow)

        assert not auth.is_active
        assert not auth.state.is_active 
        assert not grant.is_active
        assert not token.is_active


class TestTokenRequest:
    def test_tokenRequester_runs_token_request(self):
        """Убедиться, что при запросе токена что-то приходит в ответ"""
        uow = FakeUnitOfWork()
        auth = model.Authorization(grants=[model.Grant("authorization_code", "test_code")])
        uow.authorizations.add(auth)
        messagebus.handle(commands.RequestToken("test_code"), uow)
        token = auth.get_active_token()
        assert token is not None

    def test_several_tokenRequests_return_different_tokens(self):
        """Проверить, что при каждом новом запросе токена, приходит другой токен
        
        То есть нет одинаковых токенов"""
        uow = FakeUnitOfWork()
        auth = model.Authorization(
            grants=[
                model.Grant("authorization_code", "test_code1"),
                model.Grant("refresh_token", "test_code2"),                
            ]
        )
        uow.authorizations.add(auth)
        [token1] = messagebus.handle(commands.RequestToken("test_code1"), uow)
        [token2] = messagebus.handle(commands.RequestToken("test_code2"), uow)
        assert not token1.access_token == token2.access_token

    def test_tokenRequest_deactivates_old_token_and_old_grant(self):
        """Проверить, что после запроса нового токена и гранта (токена обновления),
        старые токен и грант деактивированы"""
        uow = FakeUnitOfWork()
        grant = model.Grant("refresh_token", "test_code")
        token = model.Token("test_access_token")
        auth = model.Authorization(grants=[grant], tokens=[token])
        uow.authorizations.add(auth)

        assert grant.is_active
        assert token.is_active
        [access_token] = messagebus.handle(commands.RequestToken("test_code"), uow)        
        assert not grant.is_active
        assert not token.is_active
