from . import oauth_service

class OAuthRequester():
    def __init__(self, oauth: oauth_service.AbstractOAuthService) -> None:
        self.oauth_service = oauth
    
    def post(self, endpoint, data):
        return self.oauth_service.post(endpoint, data)