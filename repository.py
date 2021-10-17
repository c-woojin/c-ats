from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.orm import Session

from constants import Market, WorkerStatus
from models.worker import Worker


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, worker: Worker):
        raise NotImplementedError

    @abstractmethod
    def get(self, worker_id: str) -> Worker:
        raise NotImplementedError

    @abstractmethod
    def check_duplicate(self, market: Market) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_by_status(self, status: WorkerStatus) -> List[Worker]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, worker: Worker):
        self.session.add(worker)

    def get(self, worker_id: str) -> Worker:
        return self.session.query(Worker).filter_by(worker_id=worker_id).one()

    def check_duplicate(self, market: Market) -> bool:
        rows = self.session.query(Worker).filter_by(market=market, status=WorkerStatus.WATCHING).all()
        return True if rows else False

    def list_by_status(self, status: WorkerStatus) -> List[Worker]:
        rows = self.session.query(Worker).filter_by(status=status).all()
        return rows
