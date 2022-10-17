from . import oauth_service
from ..config import get_client_credentials, get_oauth_callback_URL
from . import exceptions
from ..domain import model

class OAuthRequester():
    """Отправить запрос на сервис и распарсить ответ"""
    def __init__(self, oauth: oauth_service.AbstractOAuthService) -> None:
        self.oauth = oauth
        self.response = {}
    
    def post(self, endpoint, data):
        response = self.oauth.post(endpoint, data)
        if response.status_code >= 400:
            raise exceptions.OAuthError(
                f"OAuth endpoint: {endpoint}, data sent: {data}, service responded: {response.text}"
            )
        self.response = response
        return self.response
    
    def get_token(self) -> model.Token:
        return model.Token(self._get_token_str())
    
    def get_grant(self) -> model.Grant:
        return model.Grant("refresh_token", self._get_grant_code())

    def _get_token_str(self):
        return self.response.json().get("access_token", None)
        # return self.response
    
    def _get_grant_code(self):
        return self.response.json().get("refresh_token", None)        
        # return self.response.get("refresh_token", None)

    
    @classmethod
    def prepare_tokenRequest_data(cls, grant):
        if grant.grant_type == "authorization_code":
            data = {
                "code": grant.code,
                "redirect_uri": get_oauth_callback_URL()
            }
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