from fastapi import Depends
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter

from ...service_layer import unit_of_work
from ...service_layer import messagebus
from ...service_layer.messagebus import commands, events
from ...service_layer.oauth.provider import OAuthProvider
from ...adapters import orm


orm.start_mappers()


oauth_router = APIRouter(
    prefix="/oauth",
    tags=["OAuth 2.0"],
    responses={404: {"description": "Not found"}},
)


async def get_provider(provider):
    return OAuthProvider(name=provider)


async def get_uow():
    return unit_of_work.SqlAlchemyUnitOfWork()


@oauth_router.get("/redirect")
async def api_get_oauth_redirect_uri(
    provider, p=Depends(get_provider), uow=Depends(get_uow)
):
    cmd = commands.CreateAuthorization("origin", provider=p)
    [state_code] = await messagebus.handle(cmd, uow)
    url = await p.get_authorize_uri(state_code)
    return RedirectResponse(url=url)


@oauth_router.get("/callback")
async def api_oauth_callback(
    state, code, p=Depends(get_provider), uow=Depends(get_uow)
):
    evt = events.AuthCodeRecieved(
        provider=p,
        state_code=state,
        grant_code=code,
    )
    results = await messagebus.handle(evt, uow)
    assert results, "You should request new authorization code!"
    [access_token] = results
    return {"access_token": access_token}
