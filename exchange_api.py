from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from models.order import Order
from constants import Market, PriceUnit, OrderType
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
    def get_prices(self, price_unit: PriceUnit, counts: int, to: datetime) -> List[Price]:
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

    def get_prices(self, price_unit: PriceUnit, counts: int, to: datetime) -> List[Price]:
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

    def get_prices(self, price_unit: PriceUnit, counts: int, to: datetime) -> List[
        Price]:
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

    def get_prices(self, price_unit: PriceUnit, counts: int, to: datetime) -> List[
        Price]:
        pass

    def get_balance(self) -> float:
        pass

    def make_valid_order_price(self, order_type: OrderType, price: float) -> float:
        pass


class FakeExchangeAPI(AbstractExchangeAPI):
    def __init__(self, market: Market):
        super().__init__(market)
        self._orders = list()

    def buy_order(self, price: float, budget: int) -> Order:
        order = Order()
        self._orders.append(order)
        return order

    def sell_order(self, price: float, volume: float) -> Order:
        order = Order()
        self._orders.append(order)
        return order

    def cancel_order(self, order_id: str) -> str:
        pass

    def get_order(self, order_id: str) -> Order:
        pass

    def get_orders(self, order_ids: List[str]) -> List[Order]:
        pass

    def get_prices(self, price_unit: PriceUnit, counts: int, to: datetime) -> List[
        Price]:
        pass

    def get_balance(self) -> float:
        pass

    def make_valid_order_price(self, order_type: OrderType, price: float) -> float:
        pass