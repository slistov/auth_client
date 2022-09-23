"""Паттерн Репозиторий

Абстракция над хранилищем"""

import abc
from src.auth_client.adapters import orm
from src.auth_client.domain import model


class AbstractRepository(abc.ABC):
    """Абстрактный репозиторий
    """
    def add(self, auth: model.Authorization) -> model.Authorization:
        self._add(auth)

    def get_by_grant_code(self, code) -> model.Authorization:
        auth = self._get_by_grant_code(code)
        return auth

    def get_by_token(self, token) -> model.Authorization:
        auth = self._get_by_token(token)
        return auth

    @abc.abstractmethod
    def _add(self, auth: model.Authorization):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_state_code(self, code) -> model.Authorization:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_grant_code(self, code) -> model.Authorization:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_token(self, token) -> model.Authorization:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()        
        self.session = session

    def _add(self, auth: model.Authorization):
        self.session.add(auth)

    def _get_by_state_code(self, code) -> model.Authorization:
        return (
            self.session.query(model.Authorization)
            .join(model.State)
            .filter(orm.states.code == code)
            .first()
        )

    def _get_by_grant_code(self, code) -> model.Authorization:
        return (
            self.session.query(model.Authorization)
            .join(model.Grant)
            .filter(orm.grants.code == code)
            .first()
        )


    def _get_by_token(self, token) -> model.Authorization:
        return (
            self.session.query(model.Authorization)
            .join(model.Token)
            .filter(orm.tokens.token == token)
            .first()
        )
