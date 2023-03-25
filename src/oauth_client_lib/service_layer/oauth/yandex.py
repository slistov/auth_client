from .provider import OAuthProvider


class OAuthYandexProvider(OAuthProvider):
    def __init__(
        self,
    ):
        super().__init__(
            "yandex",
        )
