"""Команды
"""

from dataclasses import dataclass
from typing import Any
from ..domain import model


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
    provider: Any


@dataclass
class RequestToken(Command):
    """Запросить токен по гранту"""

    grant_code: str = None
    token: str = None
