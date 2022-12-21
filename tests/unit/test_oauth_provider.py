from src.oauth_client_lib.service_layer.oauth_provider import OAuthProvider


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

    def test_authorize_uri_contains_state(sefl):
        pass

    def test_accepts_code_if_state_is_valid(self):
        pass

    def test_denies_code_if_state_is_invalid(self):
        pass

    def test_requests_token_after_code_accepted(self):
        pass

    def test_requests_email_using_token(self):
        pass
