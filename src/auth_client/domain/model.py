class State():
    code: str = None

    def get_code(self):
        if not self.code:
            self.code = "some_code"
        return self.code


class Token():
    access_token: str = None
    def __init__(self, auth_service) -> None:
        self.auth_service = auth_service

    def get_access_token(self):
        if not self.access_token:
            self.access_token = self.auth_service.get_token()
        return self.access_token
