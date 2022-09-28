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
class ProcessAuthCodeRecieved(Command):
    """Обработать код авторизации
    
    Возникает, когда на точку входа API приходит код авторизации.
    """
    state_code: str
    auth_code: str
