import datetime
from secrets import token_urlsafe


class State:
    """Обслуживание state

    State-код отправляется на сервис авторизации при ЗАПРОСЕ кода авторизации,
    а также принимается от сервиса авторизации при ПОЛУЧЕНИИ кода авторизации.

    Бизнес-правило: state-код нельзя использовать дважды

    Модель используется в п.1-2  полного сценария, см. README.md"""
    def __init__(self, state: str = None) -> None:
        if not state:
            state = self._generate_state()
        self.state = state
        self.created = datetime.datetime.utcnow()
        self.is_active = True
        self.events = []  # """ type: List[events.Event]            

    def deactivate(self):
        self.is_active = False

    def _generate_simple_token(self, len=None):
        return token_urlsafe(len)

    def _generate_state(self):
        return self._generate_simple_token()
