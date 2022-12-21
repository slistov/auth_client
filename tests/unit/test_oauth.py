from ..conftest import FakeOAuthProvider


class TestOAuthRequest:
    def test_oauthRequester_sends_request(self):
        fake_oauth_provider = FakeOAuthProvider("http://fake.oauth.service/api")
        oauth = OAuthRequester(fake_oauth_provider)

        data = {"param1": "value1", "param2": "value2"}
        results = oauth.post(endpoint="/token", data=data)

        assert fake_oauth_provider.url == "http://fake.oauth.service/api/token"
        assert fake_oauth_provider.data == data

    def test_oauthRequester_recieves_response_from_oauth(self):
        fake_oauth_provider = FakeOAuthProvider("http://fake.oauth.service/api")
        oauth = OAuthRequester(fake_oauth_provider)

        data = {"code": "test_code", "param2": "value2"}
        results = oauth.post(endpoint="/token", data=data)

        assert results == {'access_token': 'test_access_token_for_grant_test_code', 'refresh_token': 'test_refresh_token'}
