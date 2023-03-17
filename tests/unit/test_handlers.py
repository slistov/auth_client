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
        access_token = await handlers.request_token(cmd=cmd, uow=uow)
        assert access_token == auth_wStateGrant.get_active_token().access_token
        assert not grant_authCode.is_active


class TestBusinessRestrictions:
    @pytest.mark.asyncio
    async def test_auth_code_recieved_but_inactive_state_provided(
        self,
        uow: AbstractUnitOfWork,
        state: model.State,
        grant_authCode: model.Grant,
        token: model.Token,
        auth_wStateGrantToken: model.Authorization,
    ):
        """State could be used only once
        If inactive (already used) state provided,
        then revoke authorization and stop process:
        user must begin auth process again"""
        state.is_active = False
        grant_authCode.is_active = True
        token.is_active = True

        uow.authorizations.add(auth_wStateGrantToken)
        evt = events.AuthCodeRecieved(
            grant_code="fakefake_code", state_code=state.state
        )
        with pytest.raises(exceptions.InactiveState, match="State is inactive"):
            code = await handlers.auth_code_recieved(evt=evt, uow=uow)

        auth = uow.authorizations._get_not_validated(state_code=evt.state_code)
        # authorization must be revoked
        assert not auth.is_active
        assert not state.is_active
        assert not grant_authCode.is_active
        assert not token.is_active

    @pytest.mark.asyncio
    async def test_wrong_stateCode_raises_InvalidState_exception(
        self, uow: AbstractUnitOfWork, state, auth_wState
    ):
        uow.authorizations.add(auth_wState)
        evt = events.AuthCodeRecieved(
            grant_code="possibly_fake_code", state_code="wrong_state"
        )

        with pytest.raises(exceptions.InvalidState, match="State is invalid"):
            code = await handlers.auth_code_recieved(evt=evt, uow=uow)

    @pytest.mark.asyncio
    async def test_tokenRequest_deactivates_old_token_and_old_grant(
        self,
        test_provider,
        uow: AbstractUnitOfWork,
        grant_authCode: model.Grant,
        token: model.Token,
        grant_refresh: model.Grant,
        auth_wStateGrantToken,
    ):
        """After token request: old grant and old access_token
        must be inactive
        """
        uow.authorizations.add(auth_wStateGrantToken)
        old_grant = grant_refresh
        old_token = token

        assert old_grant.is_active
        assert old_token.is_active
        access_token = await handlers.request_token(
            commands.RequestToken(grant_code=old_grant.code, oauth=test_provider), uow
        )
        assert not old_grant.is_active
        assert not old_token.is_active
