class Token:
    def __init__(self, auth_service) -> None:
        self.auth_service = auth_service
        self.access_token = None

    def get_access_token(self):
        if not self.access_token:
            self.access_token = self.auth_service.get_token()
        return self.access_token
