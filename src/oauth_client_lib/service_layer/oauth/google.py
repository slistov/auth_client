from .provider import OAuthProvider
import google.oauth2.credentials
import google_auth_oauthlib.flow
from ...entrypoints import config


class OAuthGoogleProvider(OAuthProvider):
    async def __init__(
        self,
    ):
        super().__init__(
            "google",
        )

    async def _get_authorization_url(self, state_code):
        # Use the client_secret.json file to identify the application requesting
        # authorization. The client ID (from that file) and access scopes are required.
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            "client_secret_google.json",
            scopes=self.scopes,
        )

        # Indicate where the API server will redirect the user after the user completes
        # the authorization flow. The redirect URI is required. The value must exactly
        # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
        # configured in the API Console. If this value doesn't match an authorized URI,
        # you will get a 'redirect_uri_mismatch' error.
        flow.redirect_uri = self._get_oauth_callback_URL()

        # Generate URL for request to Google's OAuth 2.0 server.
        # Use kwargs to set optional request parameters.
        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type="offline",
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes="true",
            state=state_code,
        )
        return authorization_url

    async def _get_user_info(self):
        # client = google.oauth2.
        return await super()._get_user_info()
