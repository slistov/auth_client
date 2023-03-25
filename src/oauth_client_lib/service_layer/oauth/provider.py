from urllib.parse import urlencode

import aiohttp
import json

from ...entrypoints.config import get_oauth_callback_URL
from ...service_layer import exceptions
from ...entrypoints import config


class OAuthProvider:
    def __init__(
        self,
        name,
        client_id="",
        client_secret="",
        code_url=None,
        token_url=None,
        userinfo_url=None,
        scopes=[],
        public_keys_url="",
    ):
        self.name = name
        if not (scopes and code_url and token_url and userinfo_url and public_keys_url):
            (
                _scopes,
                _code_url,
                _token_url,
                _userinfo_url,
                _public_keys_url,
            ) = self.__class__._get_provider_params(name=self.name)

        self.code_url = code_url if code_url else _code_url
        self.token_url = token_url if token_url else _token_url
        self.scopes = scopes if scopes else _scopes
        self.public_keys_url = public_keys_url if public_keys_url else _public_keys_url

        if not (client_id and client_secret):
            (_client_id, _client_secret) = self.__class__._get_oauth_secrets(self.name)
        self.client_id = client_id if client_id else _client_id
        self.client_secret = client_secret if client_secret else _client_secret

    @staticmethod
    def _get_provider_params(name):
        scopes, urls = config.get_oauth_params(name)
        return (
            scopes,
            urls["code"],
            urls["token"],
            urls["userinfo"],
            urls["public_keys"],
        )

    @staticmethod
    def _get_oauth_secrets(provider):
        with open(f"client_secret_{provider}.json") as f:
            secrets = json.load(f)["web"]
            return secrets["client_id"], secrets["client_secret"]

    async def get_authorization_url(self, state_code):
        return self._get_authorization_url(state_code)

    async def request_token(self, grant) -> aiohttp.ClientResponse.json:
        data = self._get_data_for_token_request(grant=grant)
        return await self._post(url=self.token_url, data=data)

    def _get_data_for_token_request(self, grant):
        if grant.grant_type == "authorization_code":
            data = {"code": grant.code, "redirect_uri": self._get_oauth_callback_URL()}
        elif grant.grant_type == "refresh_token":
            data = {"refresh_token": grant.code}
        else:
            raise exceptions.InvalidGrant(
                f"Unknown grant type {grant.grant_type} while requesting token"
            )

        assert self.client_id, "Token request: client_id not provided"
        assert self.client_secret, "Token request: client_secret not provided"
        data.update(
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": grant.grant_type,
            }
        )
        return data

    def _get_oauth_callback_URL(self):
        return get_oauth_callback_URL()

    def _get_authorization_url(self, state_code):
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self._get_oauth_callback_URL(),
            "scope": " ".join(self.scopes),
            "state": state_code,
        }
        uri = f"{self.code_url}?{urlencode(params,)}"
        return uri

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
