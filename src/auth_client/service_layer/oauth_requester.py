from . import oauth_service
from ..config import get_client_credentials
from . import exceptions
from ..domain import model

class OAuthRequester():
    """Отправить запрос на сервис и распарсить ответ"""
    def __init__(self, oauth: oauth_service.AbstractOAuthService) -> None:
        self.oauth = oauth
        self.response = {}
    
    def post(self, endpoint, data):
        self.response = self.oauth.post(endpoint, data)
        return self.response
    
    def get_token(self) -> model.Token:
        return model.Token(self._get_token_str())
    
    def get_grant(self) -> model.Grant:
        return model.Grant("refresh_token", self._get_grant_code())

    def _get_token_str(self):
        # return self.response.get("access_token", None)
        return self.response
    
    def _get_grant_code(self):
        return self.response.get("refresh_token", None)

    
    @classmethod
    def prepare_tokenRequest_data(cls, grant):
        if grant.grant_type == "authorization_code":
            data = {"code": grant.code}
        elif grant.grant_type == "refresh_token":
            data = {"refresh_token": grant.code}
        else:
            raise exceptions.InvalidGrant(f"Unknown grant type {grant.grant_type} while requesting token")

        client_id, client_secret = get_client_credentials()
        data.update({
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": grant.grant_type
        })
        return data