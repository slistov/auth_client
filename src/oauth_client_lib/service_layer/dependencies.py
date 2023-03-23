from .oauth.provider import OAuthProvider
from .unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from .exceptions import OAuthError


async def get_provider(provider) -> OAuthProvider:
    if not provider in providers:
        raise OAuthError("Unknown provider name")
    return OAuthProvider(provider)


async def get_uow() -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork()


providers = [
    "google",
]
