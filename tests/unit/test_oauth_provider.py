from urllib.parse import parse_qs, urlparse

import pytest

from src.oauth_client_lib.domain import model
from src.oauth_client_lib.service_layer.unit_of_work import AbstractUnitOfWork
from src.oauth_client_lib.service_layer.oauth_provider import OAuthProvider


class TestOAuthProvider:
    def test_creation(self, test_provider: OAuthProvider):
        assert test_provider.name == 'test_oauth_provider'
        assert test_provider.code_url == 'https://accounts.test.com/o/oauth2/v2/auth'
        assert test_provider.scopes == [
            'https://www.testapis.com/auth/userinfo.email',
            'openid'
        ]
        assert test_provider.token_url == 'https://oauth2.testapis.com/token'
        assert test_provider.public_keys_url == 'https://www.testapis.com/oauth2/v3/certs'

    @pytest.mark.asyncio
    async def test_returns_authorize_uri(
        self,
        uow: AbstractUnitOfWork, 
        test_provider: OAuthProvider
    ):
        assert await test_provider.get_authorize_uri(uow=uow) == 'https://accounts.test.com/o/oauth2/v2/auth?response_type=code&client_id=test_client_id&redirect_uri=https%3A%2F%2Ftest-client%2Fapi%2Foauth%2Fcallback&scope=https%3A%2F%2Fwww.testapis.com%2Fauth%2Fuserinfo.email+openid&state=some_state_code'

    @pytest.mark.asyncio
    async def test_authorize_uri_contains_state(
        self,
        uow: AbstractUnitOfWork,
        test_provider: OAuthProvider
    ):
        url = await test_provider.get_authorize_uri(uow=uow)
        parsed = urlparse(url=url)
        params = parse_qs(parsed.query)
        assert params["state"][0] == 'some_state_code'

    @pytest.mark.asyncio
    async def test_exchanges_grant_for_token(
        self,
        uow: AbstractUnitOfWork,
        test_provider: OAuthProvider
    ):
        grant = model.Grant('authorization_code', 'test_code')
        state = model.State('test_state')
        auth = model.Authorization(state=state, grants=[grant, ])
        uow.authorizations.add(auth=auth)

        response = await test_provider.request_token(grant=grant)
        assert response.status_code == 200
        assert response.json()['access_token'] == 'test_access_token_for_grant_test_code'
        assert response.json()['refresh_token'] == 'test_refresh_token'

    def test_requests_email_using_token(self):
        pass
