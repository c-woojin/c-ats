from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from cats.domain.constants import OrderType, OrderStatus


@dataclass
class Order:
    order_id: str
    type: OrderType
    status: OrderStatus
    price: float
    ordered_volume: float
    executed_volume: float
    paid_fee: float
    ordered_time: datetime

    def __eq__(self, other: Order) -> bool:  # type: ignore
        if isinstance(other, Order):
            return self.order_id == other.order_id
        return False

    def __hash__(self):
        return hash(self.order_id)
