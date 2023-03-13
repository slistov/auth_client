"""Паттерн Репозиторий

Абстракция над хранилищем"""

import abc
from . import orm
from ..domain import model
from ..service_layer import exceptions


class AbstractRepository(abc.ABC):
    """Абстрактный репозиторий
    """
    def __init__(self):
        self.seen = set()

    def add(self, auth: model.Authorization) -> model.Authorization:
        self._add(auth)
        self.seen.add(auth)

    def get(
            self,
            token=None,
            grant_code=None,
            state_code=None
    ) -> model.Authorization:
        """Get validated authorization

        Just validate auth
        """
        assert token or grant_code or state_code, "One of params must be provided"
        auth = self._get_not_validated(token, grant_code, state_code)
        if auth and auth.is_active:
            self.seen.add(auth)
            return auth

    def _get_not_validated(
            self,
            token=None,
            grant_code=None,
            state_code=None
    ) -> model.Authorization:
        """Get non-validated authorization

        Just get auth by one of provided params
        """
        if token:
            return self._get_by_token(token)
        if grant_code:
            return self._get_by_grant(grant_code)
        if state_code:
            return self._get_by_state(state_code)

    @abc.abstractmethod
    def _add(self, auth: model.Authorization):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_state(self, state) -> model.Authorization:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_grant(self, code) -> model.Authorization:
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

    def _get_by_state(self, state) -> model.Authorization:
        return (
            self.session.query(model.Authorization)
            .join(model.State)
            .filter(orm.states.c.state == state)
            .first()
        )

    def _get_by_grant_code(self, code) -> model.Authorization:
        return (
            self.session.query(model.Authorization)
            .join(model.Grant)
            .filter(orm.grants.c.code == code)
            .first()
        )

    def _get_by_token(self, token) -> model.Authorization:
        return (
            self.session.query(model.Authorization)
            .join(model.Token)
            .filter(orm.tokens.c.token == token)
            .first()
        )

    def cancel_authorization(self):
        return (
            self.session.query(model.Authorization).
            join(model.State)
        )
