from urllib.parse import urlencode

import aiohttp
import aiofiles
import json

from ...entrypoints.config import get_oauth_callback_URL
from ...service_layer import exceptions
from ...entrypoints import config


class OAuthProvider:
    def __init__(
        self,
        name,
    ):
        self.name = name

    def _get_provider_params(self):
        scopes, urls = config.get_oauth_params(self.name)
        return scopes, urls

    async def _get_oauth_secrets(self):
        async with aiofiles.open(f"client_secret_{self.name}.json") as f:
            content = await f.read()
        secrets = json.loads(content)["web"]
        return secrets["client_id"], secrets["client_secret"]

    async def get_authorization_url(self, state_code):
        return await self._get_authorization_url(state_code)

    async def request_token(self, grant) -> aiohttp.ClientResponse.json:
        data = await self._get_data_for_token_request(grant=grant)
        return await self._post(url=self._get_token_url(), data=data)

    def _get_token_url(self):
        _, urls = self._get_provider_params()
        return urls["token"]

    async def _get_data_for_token_request(self, grant):
        if grant.grant_type == "authorization_code":
            data = {"code": grant.code, "redirect_uri": self._get_oauth_callback_URL()}
        elif grant.grant_type == "refresh_token":
            data = {"refresh_token": grant.code}
        else:
            raise exceptions.InvalidGrant(
                f"Unknown grant type {grant.grant_type} while requesting token"
            )

        client_id, client_secret = await self._get_oauth_secrets()
        assert client_id, "Token request: client_id not provided"
        assert client_secret, "Token request: client_secret not provided"
        data.update(
            {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": grant.grant_type,
            }
        )
        return data

    @staticmethod
    def _get_oauth_callback_URL():
        return get_oauth_callback_URL()

    async def _get_authorization_url(self, state_code):
        params = {
            "response_type": "code",
            "client_id": await self._get_client_id(),
            "redirect_uri": self._get_oauth_callback_URL(),
            "scope": " ".join(self._get_scopes()),
            "state": state_code,
        }
        uri = f"{self._get_code_url()}?{urlencode(params,)}"
        return uri

    def _get_code_url(self):
        _, urls = self._get_provider_params()
        return urls["code"]

    async def _get_client_id(self):
        client_id, _ = await self._get_oauth_secrets()
        return client_id

    def _get_scopes(self):
        scopes, _ = self._get_provider_params()
        return scopes

    async def _post(self, url, data) -> aiohttp.ClientResponse.json:
        return await async_post(url=url, data=data)

    async def get_email(self):
        return self._get_email()

    async def _get_email(self):
        return self._get_user_info()["email"]

    async def _get_user_info(self):
        return async_get(url=self.userinfo_url)


async def async_get(url, header, params=None) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        if params:
            url = f"{url}?{urlencode(params)}"
        async with session.get(url=url, header=header) as resp:
            return await resp.json()


async def async_post(url, data) -> aiohttp.ClientResponse.json:
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=data) as resp:
            return await resp.json()
