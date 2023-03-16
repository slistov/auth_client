import pytest
from urllib.parse import urlparse, parse_qsl, unquote, urlsplit


class TestRouter:
    @pytest.mark.asyncio
    async def test_oauth_redirect(self, client):
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
