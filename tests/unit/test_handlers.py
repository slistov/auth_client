# pylint: disable=no-self-use
import pytest
from src.oauth_client_lib.domain import commands, events
from src.oauth_client_lib.service_layer import messagebus, exceptions
from src.oauth_client_lib.service_layer import handlers

from src.oauth_client_lib.domain import model
from src.oauth_client_lib.service_layer.unit_of_work import AbstractUnitOfWork


class TestHappyPaths:
    @pytest.mark.asyncio
    async def test_create_authorization_returns_state_code(
        self, uow: AbstractUnitOfWork
    ):
        """Handler create_authorization being tested"""
        cmd = commands.CreateAuthorization(
            source_url="origin", provider="test_provider"
        )
        state = await handlers.create_authorization(cmd=cmd, uow=uow)

        auth = uow.authorizations.get(state_code=state)
        assert state == auth.state.state

    @pytest.mark.asyncio
    async def test_auth_code_recieved_returns_auth_code(
        self, uow: AbstractUnitOfWork, state, grant_authCode, auth_wState
    ):
        """Handler auth_code_recieved being tested"""
        uow.authorizations.add(auth_wState)
        evt = events.AuthCodeRecieved(
            state_code=state.state, grant_code=grant_authCode.code
        )
        code = await handlers.auth_code_recieved(evt=evt, uow=uow)

        auth = uow.authorizations.get(state_code=evt.state_code)

        state = auth.state
        assert not state.is_active

        grant = auth.get_active_grant()
        assert grant.code == evt.grant_code

    @pytest.mark.asyncio
    async def test_request_token_returns_token(
        self,
        test_provider,
        uow: AbstractUnitOfWork,
        grant_authCode: model.Grant,
        auth_wStateGrant: model.Authorization,
    ):
        """Handler request_token being tested"""
        assert grant_authCode.is_active
        uow.authorizations.add(auth_wStateGrant)
        cmd = commands.RequestToken(grant_code=grant_authCode.code, oauth=test_provider)
        token = await handlers.request_token(cmd=cmd, uow=uow)
        assert token == auth_wStateGrant.get_active_token().access_token
        assert not grant_authCode.is_active


class TestBusinessRestrictions:
    @pytest.mark.asyncio
    async def test_auth_code_recieved_but_inactive_state_provided(
        self,
        uow: AbstractUnitOfWork,
        state: model.State,
        auth_wStateGrant: model.Authorization,
    ):
        """State could be used only once
        If inactive (already used) state provided,
        then revoke authorization and stop process:
        user must begin auth process again"""
        uow.authorizations.add(auth_wStateGrant)
        evt = events.AuthCodeRecieved(
            grant_code="fakefake_code", state_code=state.state
        )
        with pytest.raises(exceptions.InactiveState, match="State is inactive"):
            code = await handlers.auth_code_recieved(evt=evt, uow=uow)

        auth = uow.authorizations._get_not_validated(state_code=evt.state_code)
        # authorization must be revoked
        assert not auth.is_active

    @pytest.mark.asyncio
    async def test_with_wrong_stateCode_raises_InvalidState_exception(
        self, uow: AbstractUnitOfWork, state, auth_wState
    ):
        uow.authorizations.add(auth_wState)
        evt = events.AuthCodeRecieved(
            grant_code="possibly_fake_code", state_code="wrong_state"
        )

        with pytest.raises(exceptions.InvalidState, match="State is invalid"):
            code = await handlers.auth_code_recieved(evt=evt, uow=uow)


# class TestAccessToken:
#     @pytest.mark.asyncio
#     async def test_for_existing_authorization_by_access_token(self, uow):
#         [state_code] = await messagebus.handle(commands.CreateAuthorization("source_url"), uow)
#         await messagebus.handle(commands.ProcessGrantRecieved(state_code, "authorization_code", "test_code"), uow)
#         auth = uow.authorizations.get_by_state_code(state_code)
#         auth.tokens.append(model.Token("test_token"))

#         assert uow.authorizations.get_by_token("test_token") is not None
#         assert uow.committed

#     @pytest.mark.asyncio
#     async def test_get_active_token_for_existing_authorization(self, uow):
#         [state_code] = await messagebus.handle(commands.CreateAuthorization("source_url"), uow)
#         await messagebus.handle(commands.ProcessGrantRecieved(state_code, "authorization_code", "test_code"), uow)
#         auth = uow.authorizations.get_by_state_code(state_code)
#         auth.tokens.append(model.Token("test_token"))

#         assert auth.get_active_token().access_token == "test_token"
#         assert uow.committed


# class TestAttackHandling:
#     @pytest.mark.asyncio
#     async def test_for_existing_authorization_inactive_STATECode_deactivates_authorization_completely(self, uow):
#         [state_code] = await messagebus.handle(commands.CreateAuthorization("source_url"), uow)
#         auth = uow.authorizations.get_by_state_code(state_code)
#         grant = model.Grant("authorization_code", "test_code")
#         auth.grants.append(grant)

#         token = model.Token(access_token="test_token", expires_in=3600)
#         auth.tokens.append(token)

#         assert auth.is_active
#         assert auth.state.is_active
#         assert grant.is_active
#         assert token.is_active

#         auth.state.deactivate()
#         with pytest.raises(exceptions.InactiveState, match="State is inactive"):
#             await messagebus.handle(commands.ProcessGrantRecieved(auth.state.state, "authorization_code", "test_code"), uow)

#         assert not auth.is_active
#         assert not auth.state.is_active
#         assert not grant.is_active
#         assert not token.is_active


# class TestTokenRequest:
#     @pytest.mark.asyncio
#     async def test_tokenRequester_runs_token_request(self, test_provider, uow):
#         """Убедиться, что при запросе токена что-то приходит в ответ"""
#         auth = model.Authorization(
#             grants=[model.Grant("authorization_code", "test_code")]
#         )
#         uow.authorizations.add(auth)
#         do_request_token = commands.RequestToken("test_code", test_provider)
#         await messagebus.handle(do_request_token, uow)
#         token = auth.get_active_token()
#         assert token.access_token == 'test_access_token_for_grant_test_code'

#     @pytest.mark.asyncio
#     async def test_several_tokenRequests_return_different_tokens(self, test_provider, uow):
#         """Проверить, что при каждом новом запросе токена,
#         приходит другой токен.

#         То есть нет одинаковых токенов"""
#         auth = model.Authorization(
#             grants=[
#                 model.Grant("authorization_code", "test_code1"),
#                 model.Grant("refresh_token", "test_code2"),
#             ]
#         )
#         uow.authorizations.add(auth)
#         [token1] = await messagebus.handle(commands.RequestToken("test_code1", test_provider), uow)
#         [token2] = await messagebus.handle(commands.RequestToken("test_code2", test_provider), uow)
#         assert not token1.access_token == token2.access_token

#     @pytest.mark.asyncio
#     async def test_tokenRequest_deactivates_old_token_and_old_grant(self, test_provider, uow):
#         """Проверить, что после запроса нового токена
#         и гранта (токена обновления),
#         старые токен и грант деактивированы"""
#         grant = model.Grant("refresh_token", "test_code")
#         token = model.Token("test_access_token")
#         auth = model.Authorization(grants=[grant], tokens=[token])
#         uow.authorizations.add(auth)

#         assert grant.is_active
#         assert token.is_active
#         [access_token] = await messagebus.handle(
#             commands.RequestToken("test_code", test_provider),
#             uow
#         )
#         assert not grant.is_active
#         assert not token.is_active
