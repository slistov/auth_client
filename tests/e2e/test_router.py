from fastapi.testclient import TestClient

from oauth_client_lib import oauth_router
from oauth_client_lib.entrypoints.fastapi_app import app

app.include_router(oauth_router)
client = TestClient(app)


class TestRouter:
    def test_oauth_redirect_entrypoint(self):
        r = client.get("/oauth/redirect?provider=google")
        assert r.ok
