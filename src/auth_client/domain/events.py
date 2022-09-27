"""События
"""

# pylint: disable=too-few-public-methods
from dataclasses import dataclass
from datetime import date
from typing import Optional, Union, Literal


class Event:
    pass


@dataclass
class StateExpired(Event):
    """Код state истёк"""
    pass

@dataclass
class GrantRecieved(Event):
    """Получен грант (разрешение) на получение токена
    
    Возникает, когда на точку входа API приходит грант.
    Грант может быть разных типов:
    - код авторизации (type = "authorization_code")
    - токен обновления (type = "refresh_token")
    Вместе с кодом авторизации сервис авторизации должен прислать state.
    (шаг 2 из полного сценария, см. README.md)
    """
    state_code: Optional[str]
    grant_type: Union[Literal["authorization_code"], Literal["refresh_token"]]
    grant_code: str


@dataclass
class AuthCodeRecieved(Event):
    """Получен код авторизации
    
    Возникает, когда на точку входа API приходит код авторизации.
    """
    state_code: str
    auth_code: str


@dataclass
class RefreshTokenRecieved(Event):
    """Получен код авторизации
    
    Возникает, когда на точку входа API приходит токен обновления.
    """
    refresh_token: str
