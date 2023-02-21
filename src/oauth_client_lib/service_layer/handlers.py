"""Обработчики команд и событий

Команды и события генерируются в точках входа, см. /entrypoints
"""

from ..entrypoints import config
from ..domain import commands, events, model
from . import exceptions, oauth_provider, unit_of_work


async def create_authorization(
    cmd: commands.CreateAuthorization,
    uow: unit_of_work.AbstractUnitOfWork
) -> str:
    with uow:
        state = model.State()
        auth = model.Authorization(
            state=state,
            provider=cmd.provider
        )
        uow.authorizations.add(auth)
        uow.commit()
        return state.state


async def auth_code_recieved(
    evt: events.AuthCodeRecieved,
    uow: unit_of_work.AbstractUnitOfWork
):
    """Process authorization code recieved

    Authorization service provides an auth code,
    that must be used to request token.

    Here we save authorization code
    for authorization found by state.

    At the end, handler appends command
    for the Authorization: 'Now go and get your token!'
    """
    raise exceptions.state_exceptions.InactiveState("State is inactive")
    with uow:
        auth = uow.authorizations.get(state_code=evt.state_code)
        state = auth.state

        # Exception: are we under attack?
        if not state.is_active:
            # if we are, then invoke authorization
            auth.deactivate()
            uow.commit()
            raise exceptions.InactiveState("State is inactive")
        state.deactivate()

        # Authorization code is a grant to request token
        grant = model.Grant(
            grant_type="authorization_code",
            code=evt.grant_code
        )
        auth.grants.append(grant)
        uow.commit()
        # Now, authorization must get access token using the auth code
        auth.events.append(
            commands.RequestToken(grant_code=grant.code),
        )


async def request_token(
    cmd: commands.RequestToken,
    uow: unit_of_work.AbstractUnitOfWork
):
    """Request token from OAuth2 provider
    """
    with uow:
        auth = uow.authorizations.get(
            grant_code=cmd.grant_code,
            token=cmd.token
        )
        if not auth:
            raise exceptions.OAuthError("No active authorization found")

        old_grant = auth.get_active_grant()
        if not old_grant:
            raise exceptions.InvalidGrant(
                "No active grant found to request token"
            )
        old_grant.deactivate()

        old_token = auth.get_active_token()
        if old_token:
            old_token.deactivate()

        # We could pass custom oauth for test purposes
        oauth = cmd.oauth
        if not oauth:
            scopes, urls = config.get_oauth_params(auth.provider)
            oauth = oauth_provider.OAuthProvider(
                provider=auth.provider,
                scopes=scopes,
                code_url=urls['code'],
                token_url=urls['token'],
                public_keys_url=urls['public_keys']
            )
        r = await oauth.request_token(grant=old_grant)

        if not r:
            raise exceptions.OAuthError("Couldn't request token")

        new_token = model.Token(**r)
        auth.tokens.append(new_token)

        if "refresh_token" in r:
            new_grant = model.Grant(
                grant_type="refresh_token",
                code=r["refresh_token"]
            )
            auth.grants.append(new_grant)

        uow.commit()
        return new_token.access_token
