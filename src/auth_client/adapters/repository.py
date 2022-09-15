import abc
from src.auth_client.adapters import orm
from src.auth_client.domain import model

class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[model.State]

    def add(self, state: model.State):
        self._add(state)
        self.seen.add(state)

    def get(self, sku) -> model.State:
        state = self._get(sku)
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

    # def _get_by_batchref(self, batchref):
    #     return (
    #         self.session.query(model.State)
    #         .join(model.Batch)
    #         .filter(orm.batches.c.reference == batchref)
    #         .first()
    #     )


