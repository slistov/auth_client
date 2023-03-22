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
    provider: Any


@dataclass
class RequestToken(Command):
    """Запросить токен по гранту"""

    provider: Any
    grant_code: str = None
    token: str = None
