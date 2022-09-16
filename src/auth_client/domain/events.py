# pylint: disable=too-few-public-methods
from dataclasses import dataclass
from datetime import date
from typing import Optional


class Event:
    pass


@dataclass
class StateExpired(Event):
    pass


@dataclass
class AuthCodeRecieved(Event):
    state_code: str
    auth_code: str