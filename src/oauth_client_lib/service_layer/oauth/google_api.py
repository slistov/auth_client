from .provider import OAuthProvider


class OAuthGoogleAPIProvider(OAuthProvider):
    def __init__(self):
        super().__init__("google-api")
