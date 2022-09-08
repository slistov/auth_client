import abc

class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, obj):
        raise NotImplementedError
    
    @abc.abstractmethod
    def get(self, obj_id):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session) -> None:
        self.session = session
    