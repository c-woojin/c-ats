from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from models.worker import Worker


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, worker: Worker):
        raise NotImplementedError

    @abstractmethod
    def get(self, worker_id: str) -> Worker:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, worker: Worker):
        self.session.add(worker)

    def get(self, worker_id: str) -> Worker:
        return self.session.query(Worker).filter_by(worker_id=worker_id).one()
