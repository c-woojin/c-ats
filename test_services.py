from typing import List, Callable

import pytest
from sqlalchemy.orm import Session

import services
from constants import Market, WorkerStatus
from models.worker import Worker
from repository import AbstractRepository


class FakeRepository(AbstractRepository):
    def __init__(self, workers: List[Worker]):
        self._workers = set(workers)

    def add(self, worker: Worker):
        self._workers.add(worker)

    def get(self, worker_id: str) -> Worker:
        return next(w for w in self._workers if w.worker_id == worker_id)

    def check_duplicate(self, market: Market) -> bool:
        workers = [worker for worker in self._workers if worker.market == market and worker.status == WorkerStatus.WATCHING]
        return len(workers) > 0

    def list_by_status(self, status: WorkerStatus) -> List[Worker]:
        return [worker for worker in self._workers if worker.status == status]


class FakeSession(Session):
    committed = False

    def commit(self):
        self.committed = True


def test_add_worker(get_worker: Callable[..., Worker]):
    worker = get_worker()
    repo = FakeRepository([])

    services.add_worker(worker, repo, FakeSession())
    assert repo.get(worker.worker_id) == worker


def test_add_worker_with_duplicated_error(get_worker: Callable[..., Worker]):
    worker = get_worker(market=Market.ETH, status=WorkerStatus.WATCHING)
    repo = FakeRepository([worker])

    new_worker = get_worker(market=Market.ETH, status=WorkerStatus.WATCHING)
    with pytest.raises(services.WorkerDuplicated):
        services.add_worker(new_worker, repo, FakeSession())
