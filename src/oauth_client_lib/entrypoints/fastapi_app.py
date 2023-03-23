from fastapi import FastAPI
from .routers.oauth import oauth_router


app = FastAPI()

app.include_router(prefix="/api", router=oauth_router)
