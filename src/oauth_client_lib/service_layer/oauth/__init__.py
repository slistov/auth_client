from .provider import OAuthProvider
from .google import OAuthGoogleProvider
from .google_api import OAuthGoogleAPIProvider
from .yandex import OAuthYandexProvider

OAuthProviders = {
    "google": OAuthGoogleProvider,
    "google-api": OAuthGoogleAPIProvider,
    "yandex": OAuthYandexProvider,
}
