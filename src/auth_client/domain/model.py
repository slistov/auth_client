import datetime
from typing import Union, Literal

class State:
    def __init__(self, code: str = None) -> None:
        if not code:
            self.code = self._generate_code()
            self.created = datetime.datetime.utcnow()
            self.is_active = True
        else:
            self.code = code
    
    def _generate_code(self):
        return "some_code"
    
    def is_valid(self):
        pass

    def deactivate(self):
        self.is_active = False

class Grant:
    grant_type = Union[Literal("authorization_code"), Literal("refresh_token")]

    def __init__(self, grant_type: grant_type, code: str) -> None:
        self.grant_type = grant_type
        self.code = code
        self.created = datetime.datetime.utcnow()
        self.is_active = True        


class Token:
    def __init__(self, auth_service) -> None:
        self.auth_service = auth_service
        self.access_token = None

    def get_access_token(self):
        if not self.access_token:
            self.access_token = self.auth_service.get_token()
        return self.access_token
