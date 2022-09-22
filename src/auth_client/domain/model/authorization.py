"""Агрегат для бизнес-процесса получения токена

Получить state

Получить код авторизации
- валидировать state
- деактивировать state
- принять код, связав его со state
"""

from typing import List

from .state import State
from .grant import Grant
from .token import Token

class Authorization:
    def __init__(self, state: State = State(), grants: List[Grant] = None, tokens: List[Token] = None):
        self.state = state
        self.grants = grants if grants else []
        self.tokens = tokens if tokens else []
        self.events = []

    