from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict
from uuid import uuid4

from arrow import Arrow
from faker import Faker

from cats.domain.models.order import Order
from cats.domain.constants import Market, PriceUnit, OrderType, OrderStatus
from cats.domain.values import Price


class APIError(Exception):
    pass


class AbstractExchangeAPI(ABC):
    def __init__(self, market: Market):
        self.market = market

    @abstractmethod
    def buy_order(self, price: float, budget: int) -> Order:
        raise NotImplementedError

    @abstractmethod
    def sell_order(self, price: float, volume: float) -> Order:
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_order(self, order_id: str) -> Order:
        raise NotImplementedError

    @abstractmethod
    def get_orders(self, order_ids: List[str]) -> List[Order]:
        raise NotImplementedError

    @abstractmethod
    def get_prices(
        self, price_unit: PriceUnit, counts: int, to: Optional[datetime] = None
    ) -> List[Price]:
        raise NotImplementedError

    @abstractmethod
    def get_balance(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def make_valid_order_price(self, order_type: OrderType, price: float) -> float:
        raise NotImplementedError


class UpbitExchangeAPI(AbstractExchangeAPI):
    def buy_order(self, price: float, budget: int) -> Order:
        pass

    def sell_order(self, price: float, volume: float) -> Order:
        pass

    def cancel_order(self, order_id: str) -> str:
        pass

    def get_order(self, order_id: str) -> Order:
        pass

    def get_orders(self, order_ids: List[str]) -> List[Order]:
        pass

    def get_prices(
        self, price_unit: PriceUnit, counts: int, to: Optional[datetime] = None
    ) -> List[Price]:
        pass

    def get_balance(self) -> float:
        pass

    def make_valid_order_price(self, order_type: OrderType, price: float) -> float:
        pass


class BithumbExchangeAPI(AbstractExchangeAPI):
    def buy_order(self, price: float, budget: int) -> Order:
        pass

    def sell_order(self, price: float, volume: float) -> Order:
        pass

    def cancel_order(self, order_id: str) -> str:
        pass

    def get_order(self, order_id: str) -> Order:
        pass

    def get_orders(self, order_ids: List[str]) -> List[Order]:
        pass

    def get_prices(
        self, price_unit: PriceUnit, counts: int, to: Optional[datetime] = None
    ) -> List[Price]:
        pass

    def get_balance(self) -> float:
        pass

    def make_valid_order_price(self, order_type: OrderType, price: float) -> float:
        pass


class CoinoneExchangeAPI(AbstractExchangeAPI):
    def buy_order(self, price: float, budget: int) -> Order:
        pass

    def sell_order(self, price: float, volume: float) -> Order:
        pass

    def cancel_order(self, order_id: str) -> str:
        pass

    def get_order(self, order_id: str) -> Order:
        pass

    def get_orders(self, order_ids: List[str]) -> List[Order]:
        pass

    def get_prices(
        self, price_unit: PriceUnit, counts: int, to: Optional[datetime] = None
    ) -> List[Price]:
        pass

    def get_balance(self) -> float:
        pass

    def make_valid_order_price(self, order_type: OrderType, price: float) -> float:
        pass


class FakeExchangeAPI(AbstractExchangeAPI):
    def __init__(self, market: Market):
        super().__init__(market)
        self.fee_rate: float = 0.0005
        self._orders: List[Order] = list()

    def buy_order(self, price: float, budget: int) -> Order:
        order = Order(
            order_id=str(uuid4()),
            type=OrderType.BUY,
            status=OrderStatus.WAIT,
            price=price,
            ordered_volume=(budget * (1 - self.fee_rate)) / price,
            executed_volume=0.0,
            paid_fee=0.0,
            ordered_time=datetime.now(),
        )
        self._orders.append(order)
        return order

    def sell_order(self, price: float, volume: float) -> Order:
        order = Order(
            order_id=str(uuid4()),
            type=OrderType.SELL,
            status=OrderStatus.WAIT,
            price=price,
            ordered_volume=volume,
            executed_volume=0.0,
            paid_fee=0.0,
            ordered_time=datetime.now(),
        )
        self._orders.append(order)
        return order

    def cancel_order(self, order_id: str) -> str:
        pass

    def get_order(self, order_id: str) -> Order:
        pass

    def get_orders(self, order_ids: List[str]) -> List[Order]:
        orders = [order for order in self._orders if order.order_id in order_ids]
        results = list()
        for order in orders:
            if order.status == OrderStatus.WAIT:
                order.status = OrderStatus.DONE
            results.append(order)
        return results

    def get_prices(
        self, price_unit: PriceUnit, counts: int, to: Optional[datetime] = None
    ) -> List[Price]:
        time_units: Dict[PriceUnit, str] = {
            PriceUnit.MINUTE: "minutes",
            PriceUnit.HOUR: "hours",
            PriceUnit.DAY: "days",
        }
        now = Arrow.now().floor(time_units[price_unit])  # type: ignore
        return [
            Price(
                date_time=now.shift(**{time_units[price_unit]: -i}).datetime,
                high_price=Faker().pyfloat(),
                low_price=Faker().pyfloat(),
                trade_price=Faker().pyfloat(),
            )
            for i in range(counts)
        ]

    def get_balance(self) -> float:
        return Faker().pyfloat()

    def make_valid_order_price(self, order_type: OrderType, price: float) -> float:
        pass
