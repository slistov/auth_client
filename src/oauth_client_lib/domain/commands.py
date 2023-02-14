"""Команды
"""

from dataclasses import dataclass
from typing import Any


class Command:
    pass


# @dataclass
# class CreateState(Command):
#     source_url: str


# @dataclass
# class ValidateState(Command):
#     code: str


@dataclass
class CreateAuthorization(Command):
    source_url: str
    provider: str
    # state_code: str


# @dataclass
# class CancelAuthorization(Command):
#     """Отозвать авторизацию
    
#     Возникает в случаях
#     - пользователь отзывает авторизацию
#     - заподозрена атака (использован неактивный state, token, refresh_token)"""
#     state_code: str


@dataclass
class ProcessGrantRecieved(Command):
    """Обработать полученный грант

    Грант - разрешение на получение токена доступа:
    - типы 
        - "authorization_code" (код авторизации)
        - "refresh_token" (токен обновления)
    """
    state: str
    type: str
    code: str


@dataclass
class RequestToken(Command):
    """Запросить токен по гранту"""
    grant_code: str = None
    token: str = None
    oauth: Any = None
