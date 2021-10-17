from dataclasses import astuple
from typing import Callable

from sqlalchemy.orm import Session

from constants import WorkerStatus
from models.order import Order
from models.worker import Worker


def test_order_mapper_can_load_orders(
    session: Session, get_order: Callable[..., Order]
):
    o = get_order()
    session.execute(
        "INSERT INTO orders (order_id, type, status, price, ordered_volume, "
        "executed_volume, paid_fee, ordered_time) VALUES"
        f'("{o.order_id}", "{o.type}", "{o.status}", "{o.price}", "{o.ordered_volume}",'
        f'"{o.executed_volume}", "{o.paid_fee}", "{o.ordered_time}")'
    )
    assert session.query(Order).all() == [o]


def test_order_mapper_can_save_orders(
    session: Session, get_order: Callable[..., Order]
):
    o = get_order()
    session.add(o)
    session.commit()

    rows = list(session.execute('SELECT * FROM "orders"'))
    o.ordered_time = o.ordered_time.strftime("%Y-%m-%d %H:%M:%S.%f")  # type: ignore
    assert rows == [astuple(o)]


def test_retrieving_workers(session: Session, get_worker: Callable[..., Worker]):
    w = get_worker()
    session.execute(
        "INSERT INTO workers (worker_id, market, status, budget, exchange) VALUES  "
        f'("{w.worker_id}", "{w.market}", "{w.status}", "{w.budget}", "{w.exchange}")'
    )
    w.market = w.market.value  # type: ignore
    w.status = w.status.value  # type: ignore
    w.exchange = w.exchange.value  # type: ignore
    assert session.query(Worker).all() == [w]


def test_saving_workers(session: Session, get_worker: Callable[..., Worker]):
    w = get_worker()
    session.add(w)
    session.commit()
    rows = session.execute('SELECT * FROM "workers"')
    assert list(rows) == [(w.worker_id, w.market, w.status, w.budget, w.exchange)]


def test_updating_workers(session: Session, get_worker: Callable[..., Worker]):
    w = get_worker(status=WorkerStatus.WATCHING)
    session.add(w)
    session.commit()

    w.status = WorkerStatus.BUYING
    session.add(w)
    session.commit()
    rows = session.execute('SELECT worker_id, status FROM "workers"')
    assert list(rows) == [(w.worker_id, w.status)]
