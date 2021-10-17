from typing import Callable, Optional

import pytest
from faker import Faker

from constants import OrderType, OrderStatus
from models.order import Order


@pytest.fixture
def get_order() -> Callable:
    def _get_order(status: Optional[OrderStatus]) -> Order:
        return _order(status=status)

    return _get_order


def _order(status: Optional[OrderStatus]) -> Order:
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
