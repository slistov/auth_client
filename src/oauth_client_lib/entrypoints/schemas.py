from pydantic import BaseModel, EmailStr


class callback_query(BaseModel):
    state: str
    code: str
