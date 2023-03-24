from fastapi import Depends
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter

from ...service_layer import messagebus
from ...service_layer.messagebus import commands, events
from ...adapters import orm
from ...service_layer.dependencies import get_uow, get_provider


orm.start_mappers()


oauth_router = APIRouter(
    prefix="/oauth",
    tags=["OAuth 2.0"],
    responses={404: {"description": "Not found"}},
)


@oauth_router.get("/redirect")
async def api_get_oauth_redirect_uri(
    provider, p=Depends(get_provider), uow=Depends(get_uow)
):
    cmd = commands.CreateAuthorization(source_url="origin", provider=p)
    [state_code] = await messagebus.handle(cmd, uow)
    url = await p.get_authorization_url(state_code)
    return RedirectResponse(url=url)


@oauth_router.get("/callback")
async def api_oauth_callback(state, code, uow=Depends(get_uow)):
    evt = events.AuthCodeRecieved(
        state_code=state,
        grant_code=code,
    )
    results = await messagebus.handle(evt, uow)
    assert results, "You should request new authorization code!"
    [access_token] = results
    return {"access_token": access_token}
