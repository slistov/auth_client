from .oauth import OAuthProvider, OAuthProviders
from .unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from .exceptions import OAuthError


def get_provider(provider) -> OAuthProvider:
    if not provider in OAuthProviders:
        raise OAuthError("Unknown provider name")
    return OAuthProviders[provider]()


def get_uow() -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork()
