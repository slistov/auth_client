import datetime


class State:
    def __init__(self, code: str = None) -> None:
        if not code:
            self.code = "some_code"
            self.created = datetime.datetime.utcnow()
            self.is_active = True
        else:
            self.code = code


class Token:
    def __init__(self, auth_service) -> None:
        self.auth_service = auth_service
        self.access_token = None

    def get_access_token(self):
        if not self.access_token:
            self.access_token = self.auth_service.get_token()
        return self.access_token
