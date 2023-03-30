from .provider import OAuthProvider
from . import schemas


class OAuthYandexProvider(OAuthProvider):
    def __init__(
        self,
    ):
        super().__init__(
            "yandex",
        )

    async def _get_email(self):
        return await self._get_user_info()["default_email"]

    async def _get_user_info(self) -> schemas.UserInfo:
        """Parse YandexUserInfo as UserInfo"""
        userinfo = schemas.YandexUserInfo(**await super()._get_user_info())
        return schemas.UserInfo(email=userinfo.default_email)

    async def _post(self, url, data) -> schemas.YandexUserInfo:
        """Parse provider post response as YandexUserInfo"""
        r = await super()._post(url, data)
        return schemas.YandexUserInfo(**r)
