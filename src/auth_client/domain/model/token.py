from datetime import timedelta, datetime

class Token:
    def __init__(
        self, 
        access_token: str, 
        expires_in: timedelta = timedelta(seconds=3600),
        is_active: bool = True
    ) -> None:
        self.access_token = access_token
        self.created = datetime.utcnow()
        self.expires_in = expires_in
        self.is_active = is_active

    def get_access_token(self):
        if not self.access_token:
            self.access_token = self.auth_service.get_token()
        return self.access_token

    def deactivate(self):
        self.is_active = False
    
    @property
    def _is_expired(self) -> bool:
        return self.created + self.expires_in < datetime.utcnow()

    @property
    def is_valid(self) -> bool:
        return not(self._is_expired) and self.is_active

    