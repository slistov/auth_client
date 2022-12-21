from ..config import get_oauth_callback_URL, get_client_credentials
from . import exceptions
from ..domain import model
from typing import List
from urllib.parse import urlencode


class OAuthProvider:
    def __init__(
        self,
        name,
        code_url,
        token_url,
        scopes=[],
        public_keys_url='',
        public_keys: List[dict] = [],
        state=None
    ):
        self.name = name
        self.code_url = code_url
        self.token_url = token_url
        self.scopes = scopes
        self.public_keys_url = public_keys_url
        self.public_keys = public_keys
        state = model.State(state)
        self.authorization = model.Authorization(state=state)

    def get_authorize_uri(self):
        assert self.code_url
        params = self._get_authorize_params()
        return f"{self.code_url}?{urlencode(params)}"
###############################    
    def _get_authorize_params(self):
        client_id, _ = get_client_credentials()
        return {
            "response_type": "code",
            "state": self.authorization.state.state,
            "redirect_uri": get_oauth_callback_URL(),
            "client_id": client_id
        }
    def post(self, endpoint, data):
        return self._post(endpoint, data)

    @property
    def url(self):
        return self._url

    @property
    def _params(self):
        return self.params

    @classmethod
    def _get_tokenRequest_data(cls, grant):
        if grant.grant_type == "authorization_code":
            data = {
                "code": grant.code,
                "redirect_uri": get_oauth_callback_URL()
            }
        elif grant.grant_type == "refresh_token":
            data = {"refresh_token": grant.code}
        else:
            raise exceptions.InvalidGrant(f"Unknown grant type {grant.grant_type} while requesting token")

        client_id, client_secret = get_client_credentials()
        data.update({
            "client_id": client_id,
            "client_secret": client_secret,
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
#     async def _post(self, endpoint, data):
#         async with aiohttp.ClientSession() as session:
#             self._url = f"{self.service_url}{endpoint}"
#             response = session.post(
#                 url=self._url,
#                 data=data
#             )
#             return response.json()

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
