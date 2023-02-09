from fastapi import FastAPI, Depends
from urllib.parse import urlencode

from ..domain import commands
from ..service_layer import unit_of_work
from ..service_layer import messagebus

from ..adapters import orm
from ..config import config

from . import schemas

app = FastAPI()
orm.start_mappers()
