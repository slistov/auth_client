from fastapi import Depends
from .oauth import OAuthProvider, OAuthProviders
from .unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from .exceptions import OAuthError
from ..domain import model

from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_provider(provider) -> OAuthProvider:
    if not provider in OAuthProviders:
        raise OAuthError("Unknown provider name")
    return OAuthProviders[provider]()


def get_uow() -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork()


async def get_user_info(
    token: str = Depends(oauth2_scheme), uow: AbstractUnitOfWork = Depends(get_uow)
):
    with uow:
        auth = uow.authorizations.get(token=token)
        name = auth.provider

    p = get_provider(provider=name)
    p.access_token = token
    return await p.get_user_info()
