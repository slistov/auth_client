"""Паттерн Репозиторий

Абстракция над хранилищем"""

import abc
from src.auth_client.adapters import orm
from src.auth_client.domain import model

class AbstractRepository(abc.ABC):
    """Абстрактный репозиторий

    Помимо заглушек, ведёт список seen:
    множество объектов, с которым поработал репозиторий.
    Это множество используется для сбора и обработки всех событий в объектах множества
    """
    def __init__(self):
        self.seen = set()  #""" type: Set[model.State] 


    def add(self, state: model.State) -> model.State:
        self._add(state)
        self.seen.add(state)

    def get(self, code) -> model.State:
        state = self._get(code)
        if state:
            self.seen.add(state)
        return state

    def get_by_batchref(self, batchref) -> model.State:
        state = self._get_by_batchref(batchref)
        if state:
            self.seen.add(state)
        return state

    @abc.abstractmethod
    def _add(self, state: model.State):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, sku) -> model.State:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()        
        self.session = session

    def _add(self, state: model.State):
        self.session.add(state)

    def _get(self, code): #  -> model.State:
        return self.session.query(model.State).filter_by(code=code).first()

