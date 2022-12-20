"""Обработчики команд и событий

Команды и события генерируются в точках входа, см. /entrypoints
"""

from oauth_client_lib.domain import model, commands

from .unit_of_work import AbstractUnitOfWork
from . import exceptions
from .. import config
from . import oauth_provider


def create_authorization(
    cmd: commands.CreateAuthorization,
    uow: AbstractUnitOfWork
) -> str:
    with uow:
        state = model.State()
        auth = model.Authorization(state=state)
        uow.authorizations.add(auth)
        uow.commit()
        return state.code


def process_grant_recieved(
    cmd: commands.ProcessGrantRecieved,
    uow: AbstractUnitOfWork
):
    """Обработчик команды Обработать код авторизации
    """
    with uow:
        auth = uow.authorizations.get_by_state_code(cmd.state_code)
        if auth is None or not auth.is_active:
            raise exceptions.InvalidState("No active authorization found")

        if cmd.type == "authorization_code" and cmd.state_code:
            # Exception: are we under attack?
            if not auth.state.is_active:
                # if we are, then invoke authorization
                auth.deactivate()
                uow.commit()
                raise exceptions.InactiveState("State is inactive")
            auth.state.deactivate()

        grant = model.Grant(grant_type=cmd.type, code=cmd.code)
        auth.grants.append(grant)
        uow.commit()


def request_token(
    cmd: commands.RequestToken,
    uow: AbstractUnitOfWork
):
    with uow:
        auth = uow.authorizations.get_by_grant_code(cmd.grant_code)
        if auth is None or not auth.is_active:
            raise exceptions.InvalidGrant("No active authorization found")

        old_grant = auth.get_grant_by_code(cmd.grant_code)
        if not old_grant or not old_grant.is_active:
            raise exceptions.InvalidGrant(
                "No grant found for token requesting"
            )
        old_grant.deactivate()

        old_token = auth.get_active_token()
        if old_token:
            old_token.deactivate()

        oauth = oauth_provider.OAuthProvider(service_url=)
        token_requester = uow.get_token_requester()
        data = token_requester.prepare_tokenRequest_data(old_grant)
        token_requester.post(config.get_oauth_token_endpoint_uri(), data)

        new_token = token_requester.get_token()
        new_grant = token_requester.get_grant()
        auth.tokens.append(new_token)
        auth.grants.append(new_grant)
        uow.commit()
        return new_token
