from ...src.auth_client.domain import model


class FakeAuthService():
    def __init__(self, grant) -> None:
        self.grant = grant
   
    def _get_token_for_authCode_grant(self):
        return 'test_token_by_authCode_grant'


    def _get_token_for_refresh_grant(self):
        return 'test_token_by_refresh_grant'


    _get_token_for_grant = {
        'authorization_code': _get_token_for_authCode_grant,
        'refresh_token': _get_token_for_refresh_grant
    }

    def get_token(self):
        return self._get_token_for_grant[self.grant['type']](self)




def test__Token__sends_authCode__recieves_token_from_AuthService():
    auth_service = FakeAuthService(grant={'type':'authorization_code', 'code':'test_code'})
    token_service = model.Token(auth_service=auth_service)
    access_token = token_service.get_access_token()

    assert access_token == "test_token_by_authCode_grant"


def test__Token__sends_refreshToken__recieves_token_from_AuthService():
    auth_service = FakeAuthService(grant={'type':'refresh_token', 'code':'test_code'})
    token_service = model.Token(auth_service=auth_service)
    access_token = token_service.get_access_token()

    assert access_token == "test_token_by_refresh_grant"
