from . import oauth_service
from ..config import get_client_credentials
from .handlers import InvalidGrant

class OAuthRequester():
    def __init__(self, oauth: oauth_service.AbstractOAuthService) -> None:
        self.oauth_service = oauth
        self.oauth_response = {}
    
    def post(self, endpoint, data):
        self.oauth_response = self.oauth_service.post(endpoint, data)
        return self.oauth_response
    
    def get_token(self):
        access_token = self.oauth_response.get("access_token", None)
        return access_token
    
    def get_grant(self):
        code = self.oauth_response.get("refresh_token", None)
        return code

    
    @classmethod
    def prepare_tokenRequest_data(cls, grant):
        if grant.grant_type == "authorization_code":
            data = {"code": grant.code}
        elif grant.grant_type == "refresh_token":
            data = {"refresh_token": grant.code}
        else:
            raise InvalidGrant(f"Unknown grant type {grant.grant_type} while requesting token")

        client_id, client_secret = get_client_credentials()
        data.update({
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": grant.grant_type
        })
        return data