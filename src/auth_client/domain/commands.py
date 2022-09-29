"""Команды
"""

# pylint: disable=too-few-public-methods
from datetime import date
from typing import Optional
from dataclasses import dataclass


class Command:
    pass


@dataclass
class CreateState(Command):
    pass


@dataclass
class ValidateState(Command):
    code: str


@dataclass
class CreateAuthorization(Command):
    state_code: str


@dataclass
class CancelAuthorization(Command):
    """Отозвать авторизацию
    
    Возникает в случаях
    - пользователь отзывает авторизацию
    - заподозрена атака (использован неактивный state, token, refresh_token)"""
    state_code: str


@dataclass
class ProcessGrantRecieved(Command):
    """Обработать полученный грант

    Грант - разрешение на получение токена доступа:
    - типы 
        - "authorization_code" (код авторизации)
        - "refresh_token" (токен обновления)
    """
    state_code: Optional[str]
    type: str
    code: str


@dataclass
class ProcessTokenRecieved(Command):
    """Обработать полученный токен доступа
    """
    grant_code: str
    access_token: str