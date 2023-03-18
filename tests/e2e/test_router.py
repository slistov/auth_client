import pytest
from urllib.parse import urlparse, parse_qsl, unquote, urlsplit
from oauth_client_lib.domain import model
from oauth_client_lib.service_layer.unit_of_work import AbstractUnitOfWork


@pytest.mark.asyncio
async def test_oauth_redirect_URL_happy(client):
    """Redirect url must match specifications
    https://www.oauth.com/oauth2-servers/authorization/the-authorization-request/"""
    r = client.get("http://testserver/oauth/redirect?provider=fake_provider")

    url_query = urlsplit(r.url).query
    query = parse_qsl(url_query)

    assert (
        dict(query).items()
        >= {
            "response_type": "code",
            "client_id": "test_client_id",
            "redirect_uri": "https://test-client/api/oauth/callback",
            "scope": "https://www.testapis.com/auth/userinfo.email openid",
        }.items()
    )
    assert "state" in dict(query)
    assert dict(query)["state"]


@pytest.mark.asyncio
async def test_oauth_callback_happy(
    state: model.State,
    grant_authCode: model.Grant,
    auth_wState: model.Authorization,
    uow: AbstractUnitOfWork,
    client,
):
    """Callback endpoint
    - accepts auth code
    - requests ouathprovider for token
    - returns token recieved"""
    uow.authorizations.add(auth_wState)
    r = client.get(
        f"http://testserver/oauth/callback?state={state.state}&code={grant_authCode.code}"
    )

    url_query = urlsplit(r.url).query
    query = parse_qsl(url_query)

    assert (
        dict(query).items()
        >= {
            "response_type": "code",
            "client_id": "test_client_id",
            "redirect_uri": "https://test-client/api/oauth/callback",
            "scope": "https://www.testapis.com/auth/userinfo.email openid",
        }.items()
    )
    assert "state" in dict(query)
    assert dict(query)["state"]
