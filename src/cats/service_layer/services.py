import time

from cats.domain.constants import WorkerStatus
from cats.domain.models.worker import Worker, work
from cats.service_layer.unit_of_work import AbstractUnitOfWork


class WorkerDuplicated(Exception):
    pass


def add_worker(worker: Worker, uow: AbstractUnitOfWork):
    with uow:
        if uow.workers.check_duplicate(market=worker.market):
            raise WorkerDuplicated(f"{worker.market} is already working.")
        uow.workers.add(worker=worker)
        uow.commit()


def stat_work(uow: AbstractUnitOfWork) -> None:
    with uow:
        while watching_workers := uow.workers.list_by_status(
            status=WorkerStatus.WATCHING
        ):
            for worker in watching_workers:
                work(worker)
                uow.commit()
                time.sleep(1)
