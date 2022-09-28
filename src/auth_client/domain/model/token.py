from datetime import timedelta, datetime

class Token:
    def __init__(
        self, 
        access_token: str, 
        expires_in: timedelta
    ) -> None:
        self.access_token = access_token
        self.created = datetime.utcnow()
        self.expires_in = expires_in

    def get_access_token(self):
        if not self.access_token:
            self.access_token = self.auth_service.get_token()
        return self.access_token
