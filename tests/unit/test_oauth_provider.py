from src.oauth_client_lib.service_layer.oauth_provider import OAuthProvider
from urllib.parse import urlparse, parse_qs


class TestOAuthProvider:
    def test_creation(self, test_provider):
        assert test_provider.name == 'test_name'
        assert test_provider.code_url == 'https://accounts.test.com/o/oauth2/v2/auth'
        assert test_provider.scopes == [
            'https://www.testapis.com/auth/userinfo.email',
            'openid'
        ]
        assert test_provider.token_url == 'https://oauth2.testapis.com/token'
        assert test_provider.public_keys_url == 'https://www.testapis.com/oauth2/v3/certs'

    def test_returns_authorize_uri(self, test_provider: OAuthProvider):
        assert test_provider.get_authorize_uri()

    def test_authorize_uri_contains_state(self, test_provider: OAuthProvider):
        url = test_provider.get_authorize_uri()
        parsed = urlparse(url=url)
        params = parse_qs(parsed.query)
        assert params["state"][0] == test_provider.authorization.state.state

    def test_accepts_code_if_state_is_valid(self):
        pass

    def test_denies_code_if_state_is_invalid(self):
        pass

    def test_requests_token_after_code_accepted(self):
        pass

    def test_requests_email_using_token(self):
        pass
