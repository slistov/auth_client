from .provider import OAuthProvider


class OAuthYandexProvider(OAuthProvider):
    def __init__(
        self,
    ):
        super().__init__(
            "yandex",
        )

    async def _get_email(self):
        return await self._get_user_info()["default_email"]
