from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from uuid import uuid4

from models.order import Order
from constants import Market, PriceUnit, OrderType, OrderStatus
from values import Price


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
        self, price_unit: PriceUnit, counts: int, to: datetime
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
        self, price_unit: PriceUnit, counts: int, to: datetime
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
        self, price_unit: PriceUnit, counts: int, to: datetime
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
        self, price_unit: PriceUnit, counts: int, to: datetime
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
        self, price_unit: PriceUnit, counts: int, to: datetime
    ) -> List[Price]:
        pass

    def get_balance(self) -> float:
        pass

    def make_valid_order_price(self, order_type: OrderType, price: float) -> float:
        pass
