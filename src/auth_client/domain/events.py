"""События
"""

# pylint: disable=too-few-public-methods
from dataclasses import dataclass
from datetime import date
from typing import Optional


class Event:
    pass


@dataclass
class StateExpired(Event):
    """Код state истёк"""
    pass


@dataclass
class AuthCodeRecieved(Event):
    """Получен код авторизации
    
    Возникает, когда на точку входа API приходит код авторизации.
    Вместе с кодом авторизации сервис авторизации должен прислать state.
    (шаг 2 из полного сценария, см. README.md)

    """
    state_code: str
    auth_code: str