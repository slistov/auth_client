import abc
from src.auth_client.adapters import orm
from src.auth_client.domain import model


class AbstractRepository(abc.ABC):
    def add(self, obj):
        self._add(obj)

    def get(self, obj_code) -> model.State:
        state = self._get(obj_code)
        return state

    @abc.abstractmethod
    def _add(self, obj):
        raise NotImplementedError
    
    @abc.abstractmethod
    def _get(self, obj_id):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def _add(self, state: model.State):
        self.session.add(state)

    def _get(self, code): #  -> model.State:
        return self.session.query(model.State).filter_by(code=code).first()

    # def _get_by_batchref(self, batchref):
    #     return (
    #         self.session.query(model.Product)
    #         .join(model.Batch)
    #         .filter(orm.batches.c.reference == batchref)
    #         .first()
    #     )


