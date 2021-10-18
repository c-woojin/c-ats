from typing import List, Callable

import pytest

from cats.service_layer import services
from cats.domain.constants import Market, WorkerStatus
from cats.domain.models.worker import Worker
from cats.adapters.repository import AbstractRepository
from cats.service_layer.unit_of_work import AbstractUnitOfWork


class FakeRepository(AbstractRepository):
    def __init__(self, workers: List[Worker]):
        self._workers = set(workers)

    def add(self, worker: Worker):
        self._workers.add(worker)

    def get(self, worker_id: str) -> Worker:
        return next(w for w in self._workers if w.worker_id == worker_id)

    def check_duplicate(self, market: Market) -> bool:
        workers = [
            worker
            for worker in self._workers
            if worker.market == market and worker.status == WorkerStatus.WATCHING
        ]
        return len(workers) > 0

    def list_by_status(self, status: WorkerStatus) -> List[Worker]:
        return [worker for worker in self._workers if worker.status == status]


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self, workers: List[Worker] = []):
        self.workers = FakeRepository(workers)
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_worker(get_worker: Callable[..., Worker]):
    worker = get_worker()
    uow = FakeUnitOfWork()

    services.add_worker(worker, uow)
    assert uow.workers.get(worker.worker_id) == worker


def test_add_worker_with_duplicated_error(get_worker: Callable[..., Worker]):
    worker = get_worker(market=Market.ETH, status=WorkerStatus.WATCHING)
    uow = FakeUnitOfWork([worker])

    new_worker = get_worker(market=Market.ETH, status=WorkerStatus.WATCHING)
    with pytest.raises(services.WorkerDuplicated):
        services.add_worker(new_worker, uow)
