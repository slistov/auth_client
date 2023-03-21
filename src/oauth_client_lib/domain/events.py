"""События
"""

# pylint: disable=too-few-public-methods
from dataclasses import dataclass
from typing import Optional


class Event:
    pass


# @dataclass
# class StateExpired(Event):
#     """Код state истёк"""
#     pass


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

    # grant_type: Union[Literal["authorization_code"], Literal["refresh_token"]]
    grant_code: str


@dataclass
class AuthCodeRecieved(GrantRecieved):
    state_code: Optional[str]


@dataclass
class RefreshTokenRecieved(GrantRecieved):
    pass


# @dataclass
# class TokenRecieved(Event):
#     """Получен токен доступа

#     Возникает, когда на точку входа API приходит токен доступа"""
#     grant_code: str
#     access_token: str

# @dataclass
# class RefreshTokenRecieved(Event):
#     """Получен токен обновления

#     Возникает, когда на точку входа API приходит токен обновления.
#     """
#     refresh_token: str
