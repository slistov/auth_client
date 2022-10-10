from pydantic import BaseModel

class callback_query(BaseModel):
    state: str
    code: str