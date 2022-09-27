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
    state: str