from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter

from ...service_layer import unit_of_work
from ...service_layer import messagebus
from ...service_layer.messagebus import commands, events

oauth_router = APIRouter(
    prefix="/oauth",
    tags=["OAuth 2.0"],
    responses={404: {"description": "Not found"}},
)


@oauth_router.get("/redirect")
async def api_get_oauth_redirect_uri(provider):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    cmd = commands.CreateAuthorization("origin", provider=provider)
    [state_code] = await messagebus.handle(cmd, uow)
    url = await messagebus.get_oauth_uri(state_code)
    # return url
    return RedirectResponse(url=url)


@oauth_router.get("/callback")
async def api_oauth_callback(state, code):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    evt = events.AuthCodeRecieved(
            state_code=state,
            grant_code=code,
        )
    results = await messagebus.handle(evt, uow)
    assert results, "You should request new authorization code!"
    access_token = results[-1]
    return {"access_token": access_token}
