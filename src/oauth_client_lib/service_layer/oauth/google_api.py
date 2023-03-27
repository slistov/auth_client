from .provider import OAuthProvider


class OAuthGoogleAPIProvider(OAuthProvider):
    def __init__(self):
        super().__init__("google-api")

    def _get_provider_params(cls, name):
        return super()._get_provider_params(name)
