import time

from sqlalchemy.orm import Session

from constants import WorkerStatus
from models.worker import Worker, work
from repository import AbstractRepository


class WorkerDuplicated(Exception):
    pass


def add_worker(worker: Worker, repo: AbstractRepository, session: Session):
    if repo.check_duplicate(market=worker.market):
        raise WorkerDuplicated(f"{worker.market} is already working.")
    repo.add(worker=worker)
    session.commit()


def stat_work(repo: AbstractRepository, session: Session) -> None:
    while watching_workers := repo.list_by_status(status=WorkerStatus.WATCHING):
        for worker in watching_workers:
            work(worker)
            session.commit()
            time.sleep(1)
