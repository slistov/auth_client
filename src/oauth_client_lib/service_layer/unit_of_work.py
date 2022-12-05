# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session


from oauth_client_lib import config
from oauth_client_lib.adapters import repository
from oauth_client_lib.service_layer import oauth_requester
from oauth_client_lib.service_layer import oauth_service


class AbstractUnitOfWork(abc.ABC):
    authorizations: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        for obj in self.authorizations.seen:
            while obj.events:
                yield obj.events.pop(0)

    def get_token_requester(self):
        return self._get_token_requester()

    @abc.abstractmethod
    def _get_token_requester(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
        isolation_level="REPEATABLE READ",
    )
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()  # type: Session
        self.authorizations = repository.SQLAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def _get_token_requester(self) -> oauth_requester.OAuthRequester:
        oauth = oauth_service.OAuthService(config.get_oauth_host())
        return oauth_requester.OAuthRequester(oauth)
