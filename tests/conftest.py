import time
from pathlib import Path
from typing import Callable, Optional, Set, List

import pytest
import requests  # type: ignore
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, clear_mappers, Session

from cats import config
from cats.domain.constants import OrderType, OrderStatus, Market, WorkerStatus
from cats.domain.models.order import Order
from cats.domain.models.worker import Worker
from cats.adapters.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()


@pytest.fixture
def session(session_factory):
    return session_factory()


@pytest.fixture
def get_order() -> Callable[..., Order]:
    def _get_order(status: Optional[OrderStatus] = None) -> Order:
        return _order(status=status)

    return _get_order


def _order(status: Optional[OrderStatus] = None) -> Order:
    return Order(
        order_id=Faker().pystr(),
        type=Faker().random_element(elements=OrderType),
        status=status or Faker().random_element(elements=OrderStatus),
        price=Faker().pyfloat(),
        ordered_volume=Faker().pyfloat(),
        executed_volume=Faker().pyfloat(),
        paid_fee=Faker().pyint(),
        ordered_time=Faker().date_time(),
    )


@pytest.fixture
def get_worker() -> Callable[..., Worker]:
    def _get_worker(
        status: Optional[WorkerStatus] = None,
        orders: Optional[Set[Order]] = None,
        market: Optional[Market] = None,
    ) -> Worker:
        return _worker(status, orders, market)

    return _get_worker


def _worker(
    status: Optional[WorkerStatus] = None,
    orders: Optional[Set[Order]] = None,
    market: Optional[Market] = None,
) -> Worker:
    return Worker(
        market=market or Faker().random_element(elements=Market),
        status=status or Faker().random_element(elements=WorkerStatus),
        orders=orders or set(),
    )


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


@pytest.fixture(scope="session")
def postgres_db() -> Engine:
    engine = create_engine(config.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db) -> Session:
    start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture
def add_worker(postgres_session: Session):
    workers_added = set()

    def _add_worker(workers: List[Worker]):
        for w in workers:
            postgres_session.execute(
                "INSERT INTO workers (worker_id, market, status, budget, exchange)"
                " VALUES (:worker_id, :market, :status, :budget, :exchange)",
                dict(
                    worker_id=w.worker_id,
                    market=w.market,
                    status=w.status,
                    budget=w.budget,
                    exchange=w.exchange,
                ),
            )
            workers_added.add(w.worker_id)
        postgres_session.commit()

    yield _add_worker

    for worker_id in workers_added:
        postgres_session.execute(
            "DELETE FROM workers WHERE worker_id=:worker_id",
            dict(worker_id=worker_id),
        )
