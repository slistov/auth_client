from typing import Union, Literal
import datetime

class Grant:
    def __init__(self, grant_type: str, code: str, is_active: bool = True) -> None:
        self.grant_type = grant_type
        self.code = code
        self.created = datetime.datetime.utcnow()
        self.is_active = is_active

    def deactivate(self):
        self.is_active = False
