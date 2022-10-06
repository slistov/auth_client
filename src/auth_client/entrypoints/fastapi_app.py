from fastapi import FastAPI, Response

from auth_client.domain import commands
from auth_client.service_layer import unit_of_work, messagebus

from auth_client.adapters import orm
from auth_client import config

from urllib.parse import urlencode

app = FastAPI()
orm.start_mappers()

def get_oauth_uri(state_code):
    client_id, _ = config.get_client_credentials()

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": config.get_oauth_callback_URL(),
        "scope": config.get_scope(),
        "state": state_code
    }
    return f"{config.get_oauth_host()}?{urlencode(params)}"


@app.get('/api/oauth/authorize')
def get_oauth_authorize_uri():
    cmd = commands.CreateAuthorization()
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    results = messagebus.handle(cmd, uow)
    state_code = results.pop(0)
    return get_oauth_uri(state_code)
