class Token:
    def __init__(self, access_token) -> None:
        self.access_token = access_token

    def get_access_token(self):
        if not self.access_token:
            self.access_token = self.auth_service.get_token()
        return self.access_token
