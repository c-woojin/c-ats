from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from cats import config
from cats.adapters.repository import AbstractRepository, SqlAlchemyRepository


class AbstractUnitOfWork(ABC):
    workers: AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY: Callable[..., Session] = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
    )
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self, session_factory: Callable[..., Session] = DEFAULT_SESSION_FACTORY
    ):
        self.session_factory = session_factory

    def __enter__(self):
        self.session: Session = self.session_factory()
        self.workers = SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
