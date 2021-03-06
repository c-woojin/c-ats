from datetime import datetime
from typing import Callable
from unittest.mock import MagicMock

from cats.domain.constants import Exchange, WorkerStatus, OrderStatus
from cats.domain.models.order import Order
from cats.domain.models.worker import Worker
from cats.domain.values import Price


def test_is_buy_timing_return_true_when_trader_price_is_lower_then_average():
    p1 = Price(datetime.now(), 1000.0, 500, 600)
    p2 = Price(datetime.now(), 1100, 550, 900)
    p3 = Price(datetime.now(), 1500, 600, 600)

    worker = Worker(prices=[p1, p2, p3])
    assert worker._is_buy_timing() is True


def test_is_buy_timing_return_false_when_trader_price_is_greater_then_average():
    p1 = Price(datetime.now(), 1000.0, 500, 600)
    p2 = Price(datetime.now(), 1100, 550, 900)
    p3 = Price(datetime.now(), 1500, 600, 1500)

    worker = Worker(prices=[p1, p2, p3])
    assert worker._is_buy_timing() is False


def test_get_unit_budget_when_budget_remains():
    worker = Worker(budget="10000:20000")
    unit_budget = worker._get_unit_budget()
    assert unit_budget == 10000


def test_get_unit_budget_gets_zero_when_budget_is_empty():
    worker = Worker(budget="")
    unit_budget = worker._get_unit_budget()
    assert unit_budget == 0


def test_work_for_watching_buy_order_when_is_buy_timing_is_true():
    worker = Worker(
        exchange=Exchange.FAKE,
    )

    worker._is_buy_timing = MagicMock(return_value=True)  # type: ignore
    worker.work_for_watching()

    assert len(worker.orders) == 1
    assert worker.status == WorkerStatus.BUYING


def test_get_orders_by_status(get_order: Callable[..., Order]):
    wait_order = get_order(status=OrderStatus.WAIT)
    done_order = get_order(status=OrderStatus.DONE)
    cancel_order = get_order(status=OrderStatus.CANCEL)
    worker = Worker(
        orders={wait_order, done_order, cancel_order},
        exchange=Exchange.FAKE,
    )

    assert [wait_order] == worker._get_orders_by_status(statuses=(OrderStatus.WAIT,))
    assert [done_order] == worker._get_orders_by_status(statuses=(OrderStatus.DONE,))
    assert [cancel_order] == worker._get_orders_by_status(
        statuses=(OrderStatus.CANCEL,)
    )
    assert {wait_order, done_order, cancel_order} == set(
        worker._get_orders_by_status(
            statuses=(OrderStatus.WAIT, OrderStatus.DONE, OrderStatus.CANCEL)
        )
    )


def test_update_orders_from_api():
    worker = Worker(
        exchange=Exchange.FAKE,
    )
    order = worker._get_api().buy_order(1000, 50000)
    worker.orders.add(order)
    worker._update_orders_from_api()
    assert len(worker.orders) == 1
    assert worker.orders.pop().status == OrderStatus.DONE


def test_update_prices_from_api():
    worker = Worker(
        exchange=Exchange.FAKE,
    )
    worker._update_prices_from_api()
    assert len(worker.prices) == 24
