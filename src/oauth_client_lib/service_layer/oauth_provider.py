from ..config import get_oauth_callback_URL
from . import exceptions
from ..domain import model

from ..domain import commands
from ..service_layer import unit_of_work
from ..service_layer import messagebus
from ..config import config

from typing import List
from urllib.parse import urlencode
import aiohttp


class OAuthProvider:
    def __init__(
        self,
        name,
        code_url=None,
        token_url=None,
        scopes=[],
        public_keys_url='',
        public_keys: List[dict] = [],
        client_id='',
        client_secret=''
    ):
        self.name = name
        self.code_url = code_url
        self.token_url = token_url
        self.scopes = scopes
        self.public_keys_url = public_keys_url
        self.public_keys = public_keys

    def get_authorize_uri(self):
        assert self.code_url
        uow = unit_of_work.SqlAlchemyUnitOfWork()
        cmd = commands.CreateAuthorization("origin")
        [state_code] = messagebus.handle(cmd, uow)
        return self._get_oauth_uri(state_code)

    async def request_token(self, grant):
        data = self._get_tokenRequest_data(grant=grant)
        self.response = await post_async(
            url=self.token_url,
            data=data
        )
        return self.response

    def _get_oauth_uri(self, state_code):
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": config.get_oauth_callback_URL(),
            "scope": self.scopes,
            "state": state_code
        }
        return f"{config.get_oauth_host()}?{urlencode(params)}"

    def _get_tokenRequest_data(self, grant):
        if grant.grant_type == "authorization_code":
            data = {
                "code": grant.code,
                "redirect_uri": get_oauth_callback_URL()
            }
        elif grant.grant_type == "refresh_token":
            data = {"refresh_token": grant.code}
        else:
            raise exceptions.InvalidGrant(f"Unknown grant type {grant.grant_type} while requesting token")

        data.update({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": grant.grant_type
        })
        return data

    def _post(self, endpoint, data):
        response = self.oauth.post(endpoint, data)
        if response.status_code >= 400:
            raise exceptions.OAuthError(
                f"OAuth endpoint: {endpoint}, data sent: {data}, service responded: {response.text}"
            )
        self.response = response
        return self.response

    def get_token(self) -> model.Token:
        return model.Token(self._get_token_str())

    def get_grant(self) -> model.Grant:
        return model.Grant("refresh_token", self._get_grant_code())

    def _get_token_str(self):
        return self.response.json().get("access_token", None)
        # return self.response

    def _get_grant_code(self):
        return self.response.json().get("refresh_token", None)
        # return self.response.get("refresh_token", None)


async def post_async(url, data):
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            url=url,
            data=data
        )
        return response.json()
