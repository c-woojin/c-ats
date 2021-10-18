from typing import Callable

from sqlalchemy.orm import Session

from cats.domain.models.order import Order
from cats.domain.models.worker import Worker
from cats.adapters.repository import SqlAlchemyRepository


def test_repository_can_save_a_worker(
    session: Session, get_worker: Callable[..., Worker]
):
    w = get_worker()

    repo = SqlAlchemyRepository(session)
    repo.add(w)
    session.commit()

    rows = session.execute('SELECT * FROM "workers"')
    assert list(rows) == [(w.worker_id, w.market, w.status, w.budget, w.exchange)]


def test_repository_can_retrieve_a_worker_with_orders(
    session: Session,
    get_worker: Callable[..., Worker],
    get_order: Callable[..., Order],
):
    o = get_order()
    w = get_worker(orders={o})
    repo = SqlAlchemyRepository(session)
    repo.add(w)
    session.commit()

    retrieved = repo.get(w.worker_id)

    assert retrieved == w
    assert retrieved.orders == {o}
