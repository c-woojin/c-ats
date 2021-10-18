from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Price:
    date_time: datetime
    high_price: float
    low_price: float
    trade_price: float

    def __add__(self, other: Any) -> Price:
        if isinstance(other, Price):
            return Price(
                date_time=max(self, other).date_time,  # type: ignore
                high_price=self.high_price + other.high_price,
                low_price=self.low_price + other.low_price,
                trade_price=self.trade_price + other.trade_price,
            )
        raise TypeError

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, Price):
            return self.date_time > other.date_time
        raise TypeError
