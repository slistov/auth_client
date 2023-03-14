from urllib.parse import urlencode

import aiohttp
import json
import requests

from ..entrypoints.config import get_oauth_callback_URL
from ..domain import commands, model
from fastapi.responses import JSONResponse
from ..service_layer import messagebus, unit_of_work
from . import exceptions
from ..entrypoints import config
from ..adapters import orm

orm.start_mappers()


class OAuthProvider:
    def __init__(
        self,
        name,
        client_id='',
        client_secret='',
        code_url=None,
        token_url=None,
        scopes=[],
        public_keys_url='',
    ):
        if not (scopes and code_url and token_url and public_keys_url):
            (
                _scopes,
                _code_url,
                _token_url,
                _public_keys_url
            ) = self.__class__._get_provider_params(name=name)

        self.name = name
        self.code_url = code_url if code_url else _code_url
        self.token_url = token_url if token_url else _token_url
        self.scopes = scopes if scopes else _scopes
        self.public_keys_url = public_keys_url if public_keys_url else _public_keys_url

        if not (client_id and client_secret):
            (
                _client_id,
                _client_secret
            ) = self.__class__._get_oauth_secrets(self.name)
        self.client_id = client_id if client_id else _client_id
        self.client_secret = client_secret if client_secret else _client_secret

    @staticmethod
    def _get_oauth_secrets(provider):
        with open(f'client_secret_{provider}.json') as f:
            secrets = json.load(f)["web"]
            return secrets["client_id"], secrets["client_secret"]

    async def get_authorize_uri(self, uow=None):
        assert self.code_url, "code_url is not provided"
        uow = unit_of_work.SqlAlchemyUnitOfWork() if not uow else uow
        cmd = commands.CreateAuthorization(source_url="origin_url", provider=self.name)
        [state_code] = await messagebus.handle(cmd, uow)
        return self._get_oauth_uri(state_code)

    async def request_token(self, grant) -> requests.Response:
        data = self._get_data_for_token_request(grant=grant)
        response = await self._post(
            url=self.token_url,
            data=data
        )
        if response.ok:
            return response

    @staticmethod
    def _get_provider_params(name):
        scopes, urls = config.get_oauth_params(name)
        return scopes, urls['code'], urls['token'], urls['public_keys']

    def _get_oauth_callback_URL(self):
        return get_oauth_callback_URL()

    def _get_oauth_uri(self, state_code):
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self._get_oauth_callback_URL(),
            "scope": ' '.join(self.scopes),
            "state": state_code
        }
        uri = f"{self.code_url}?{urlencode(params,)}"
        return uri

    def _get_data_for_token_request(self, grant):
        if grant.grant_type == "authorization_code":
            data = {
                "code": grant.code,
                "redirect_uri": self._get_oauth_callback_URL()
            }
        elif grant.grant_type == "refresh_token":
            data = {"refresh_token": grant.code}
        else:
            raise exceptions.InvalidGrant(
                f"Unknown grant type {grant.grant_type} while requesting token"
            )

        assert self.client_id, "Token request: client_id not provided"
        assert self.client_secret, "Token request: client_secret not provided"
        data.update({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": grant.grant_type
        })
        return data

    async def _post(self, url, data) -> requests.Response:
        return await post_async(
            url=url,
            data=data
        )

    async def get_email(self):
        return self.auth

    # async def get_token(self) -> model.Token:
    #     return model.Token(await self._get_token_str())

    # async def get_grant(self) -> model.Grant:
    #     code = await self._get_grant_code()
    #     if code:
    #         return model.Grant("refresh_token", code)

    # async def _get_token_str(self):
    #     if self.response.ok:
    #         resp_json = await self.response.json()
    #         return resp_json.get("access_token", None)

    # async def _get_grant_code(self):
    #     if self.response.ok:
    #         resp_json = await self.response.json()
    #         return resp_json.get("refresh_token", None)


async def post_async(url, data) -> requests.Response:
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            url=url,
            data=data
        )
        return response
