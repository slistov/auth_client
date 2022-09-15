import datetime


class State:
    def __init__(self, code: str = None) -> None:
        if not code:
            self.code = self._generate_code()
            self.created = datetime.datetime.utcnow()
            self.is_active = True
            self.events = []  # type: List[events.Event]            
        else:
            self.code = code
    
    def _generate_code(self):
        return "some_code"
    
    def is_valid(self):
        pass





class Token:
    def __init__(self, auth_service) -> None:
        self.auth_service = auth_service
        self.access_token = None

    def get_access_token(self):
        if not self.access_token:
            self.access_token = self.auth_service.get_token()
        return self.access_token
