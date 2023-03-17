import pytest
from urllib.parse import urlparse, parse_qsl, unquote, urlsplit


class TestRouter:
    @pytest.mark.asyncio
    async def test_oauth_redirect_URL_correct(self, client):
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
