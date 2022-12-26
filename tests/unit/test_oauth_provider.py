import pytest
from src.oauth_client_lib.service_layer.oauth_provider import OAuthProvider
from urllib.parse import urlparse, parse_qs

class TestOAuthProvider:
    def test_creation(self, test_provider):
        assert test_provider.name == 'test_oauth_provider'
        assert test_provider.code_url == 'https://accounts.test.com/o/oauth2/v2/auth'
        assert test_provider.scopes == [
            'https://www.testapis.com/auth/userinfo.email',
            'openid'
        ]
        assert test_provider.token_url == 'https://oauth2.testapis.com/token'
        assert test_provider.public_keys_url == 'https://www.testapis.com/oauth2/v3/certs'

    @pytest.mark.asyncio
    async def test_returns_authorize_uri(self, uow, test_provider: OAuthProvider):
        assert await test_provider.get_authorize_uri(uow=uow) == 'https://accounts.test.com/o/oauth2/v2/auth?response_type=code&client_id=test_client_id&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Foauth%2Fcallback&scope=%5B%27https%3A%2F%2Fwww.testapis.com%2Fauth%2Fuserinfo.email%27%2C+%27openid%27%5D&state=some_state_code'

    def test_authorize_uri_contains_state(self, test_provider: OAuthProvider):
        url = test_provider.get_authorize_uri(state='test_state')
        parsed = urlparse(url=url)
        params = parse_qs(parsed.query)
        assert params["state"][0] == 'test_state'

    def test_exchanges_grant_for_token(self, test_provider: OAuthProvider):
        token = test_provider.exchange_grant_for_token(code='test_code')
        assert token == 'test_token'

    def test_requests_email_using_token(self):
        pass
