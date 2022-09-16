from fastapi import FastAPI

from src.auth_client.domain import commands
from src.auth_client.service_layer import unit_of_work, messagebus

from src.auth_client.adapters import orm

app = FastAPI()
orm.start_mappers()

@app.get('/api/oauth/authorize')
def authorize():
    cmd = commands.CreateState()
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    results = messagebus.handle(cmd, uow)
    state_code = results.pop(0)
    return {"state": state_code}
