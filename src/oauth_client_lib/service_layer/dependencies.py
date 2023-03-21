from .oauth_provider import OAuthProvider
from .unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from .exceptions import OAuthError


async def get_provider(**kwargs) -> OAuthProvider:
    try:
        name = kwargs["provider"]
    except KeyError:
        try:
            state_code = kwargs["state"]
            uow: AbstractUnitOfWork = kwargs["uow"]
        except KeyError:
            raise OAuthError("Unknown provider name")
        else:
            auth = uow.authorizations.get(state_code=state_code)
            name = auth.provider
    else:
        return OAuthProvider(name=name)


async def get_uow() -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork()
