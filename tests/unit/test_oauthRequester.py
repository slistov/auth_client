from auth_client.service_layer.oauth_requester import OAuthRequester
from auth_client.service_layer.oauth_service import AbstractOAuthService

class FakeOAuthService(AbstractOAuthService):
    def __init__(self, service_url) -> None:
        self.service_url = service_url
        self.endpoint = None
        self.data = None
    
    def _post(self, endpoint, data):
        self.endpoint = endpoint
        self.data = data
        return {"k1": "v1", "k2": "v2"}
    
    @property
    def _url(self):
        return f"{self.service_url}{self.endpoint}"

class TestOAuthRequest:
    def test_oauthRequester_sends_request(self):
        fake_oauth_service = FakeOAuthService("http://fake.oauth.service/api")
        oauth = OAuthRequester(fake_oauth_service)
        
        data = {"param1": "value1", "param2": "value2"}
        results = oauth.post(endpoint="/token", data=data)

        assert fake_oauth_service.url == "http://fake.oauth.service/api/token"
        assert fake_oauth_service.data == data

    def test_oauthRequester_recieves_response_from_oauth(self):
        fake_oauth_service = FakeOAuthService("http://fake.oauth.service/api")
        oauth = OAuthRequester(fake_oauth_service)
        
        data = {"param1": "value1", "param2": "value2"}
        results = oauth.post(endpoint="/token", data=data)

        assert results == {"k1": "v1", "k2": "v2"}
        