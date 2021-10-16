from datetime import datetime

from constants import Exchange, WorkerStatus
from models.worker import Worker
from values import Price


def test_is_buy_timing_return_true_when_trader_price_is_lower_then_average():
    p1 = Price(datetime.now(), 1000.0, 500, 600)
    p2 = Price(datetime.now(), 1100, 550, 900)
    p3 = Price(datetime.now(), 1500, 600, 600)

    worker = Worker(prices=[p1, p2, p3])
    assert worker.is_buy_timing() is True


def test_is_buy_timing_return_false_when_trader_price_is_greater_then_average():
    p1 = Price(datetime.now(), 1000.0, 500, 600)
    p2 = Price(datetime.now(), 1100, 550, 900)
    p3 = Price(datetime.now(), 1500, 600, 1500)

    worker = Worker(prices=[p1, p2, p3])
    assert worker.is_buy_timing() is False


def test_get_unit_budget_when_budget_remains():
    worker = Worker(budget="1000:2000")
    unit_budget = worker.get_unit_budget()
    assert unit_budget == 1000


def test_get_unit_budget_gets_zero_when_budget_is_empty():
    worker = Worker(budget="")
    unit_budget = worker.get_unit_budget()
    assert unit_budget == 0


def test_work_for_watching_buy_order_when_is_buy_timing_is_true():
    p1 = Price(datetime.now(), 1000.0, 500, 600)
    p2 = Price(datetime.now(), 1100, 550, 900)
    p3 = Price(datetime.now(), 1500, 600, 600)

    worker = Worker(
        prices=[p1, p2, p3],
        exchange=Exchange.FAKE,
    )

    worker.work_for_watching()

    assert len(worker.orders) == 1
    assert worker.status == WorkerStatus.BUYING
