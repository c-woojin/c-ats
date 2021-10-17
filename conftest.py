from typing import Callable, Optional, Set

import pytest
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from constants import OrderType, OrderStatus, Market, WorkerStatus
from models.order import Order
from models.worker import Worker
from orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


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
        status: Optional[WorkerStatus] = None, orders: Optional[Set[Order]] = None
    ) -> Worker:
        return _worker(status, orders)

    return _get_worker


def _worker(
    status: Optional[WorkerStatus] = None, orders: Optional[Set[Order]] = None
) -> Worker:
    return Worker(
        market=Faker().random_element(elements=Market),
        status=status or Faker().random_element(elements=WorkerStatus),
        orders=orders or set(),
    )
