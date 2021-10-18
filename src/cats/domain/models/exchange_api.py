from __future__ import annotations

import hashlib
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict
from urllib.parse import urlencode
from uuid import uuid4

import jwt  # type: ignore
import requests  # type: ignore
from arrow import Arrow
from faker import Faker

from cats.domain.models.order import Order
from cats.domain.constants import Market, PriceUnit, OrderType, OrderStatus
from cats.domain.values import Price


class APIError(Exception):
    pass


class AbstractExchangeAPI(ABC):
    def __init__(self, market: Market):
        self.market: str = market.value

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


DEFAULT_UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY", "access-key")
DEFAULT_UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY", "secret-key")


class UpbitExchangeAPI(AbstractExchangeAPI):
    def __init__(
        self,
        market: Market,
        access_key: str = DEFAULT_UPBIT_ACCESS_KEY,
        secret_key: str = DEFAULT_UPBIT_SECRET_KEY,
    ):
        super().__init__(market)
        self.market = f"KRW-{market}"
        self.access_key = access_key
        self.secret_key = secret_key
        self.host = "https://api.upbit.com/v1"

        self.sides = dict(
            bid=OrderType.BUY,
            ask=OrderType.SELL,
        )
        self.states = dict(
            wait=OrderStatus.WAIT,
            done=OrderStatus.DONE,
            cancel=OrderStatus.CANCEL,
        )

    def buy_order(self, price: float, budget: int) -> Order:
        valid_price = self.make_valid_order_price(
            order_type=OrderType.BUY, price=price
        )
        order = self._post_orders("bid", budget / valid_price, price)
        if "error" in order:
            raise APIError(str(order))
        return self._make_order(order)

    def sell_order(self, price: float, volume: float) -> Order:
        valid_price = self.make_valid_order_price(
            order_type=OrderType.SELL, price=price
        )
        order = self._post_orders("ask", volume, valid_price)
        if "error" in order:
            raise APIError(str(order))
        return self._make_order(order)

    def cancel_order(self, order_id: str) -> str:
        order = self._delete_order(order_id)
        if "error" in order:
            raise APIError(str(order))
        return order["uuid"]

    def get_orders(self, order_ids: List[str]) -> List[Order]:
        wait_orders = self._get_orders_by_uuids(order_ids, ["wait"])
        if "error" in wait_orders:
            raise APIError(str(wait_orders))
        cancel_or_done_orders = self._get_orders_by_uuids(
            order_ids, ["cancel", "done"]
        )
        if "error" in cancel_or_done_orders:
            raise APIError(str(cancel_or_done_orders))
        orders = wait_orders + cancel_or_done_orders
        return [self._make_order(order) for order in orders]

    def get_prices(
        self, price_unit: PriceUnit, counts: int, to: Optional[datetime] = None
    ) -> List[Price]:
        if price_unit == PriceUnit.MINUTE:
            prices = self._candles_minutes(unit=1, count=counts)
        elif price_unit == PriceUnit.HOUR:
            prices = self._candles_minutes(unit=60, count=counts)
        elif price_unit == PriceUnit.DAY:
            prices = self._candles_days(count=counts)
        else:
            raise APIError(f"Invalid price unit.({price_unit})")
        return [self._make_price(price) for price in prices]

    def get_balance(self) -> float:
        chance = self._orders_chance()
        if "error" in chance:
            raise APIError(str(chance))
        return float(chance["ask_account"]["balance"]) - float(
            chance["ask_account"]["locked"]
        )

    def make_valid_order_price(self, order_type: OrderType, price: float) -> float:
        if price >= 2000000:  # 1000
            bias = 1000.0
        elif price >= 1000000:  # 500
            bias = 500.0
        elif price >= 500000:  # 100
            bias = 100.0
        elif price >= 100000:  # 50
            bias = 50.0
        elif price >= 10000:  # 10
            bias = 10.0
        elif price >= 1000:  # 5
            bias = 5.0
        elif price >= 100:  # 1
            bias = 1.0
        elif price >= 10:  # 0.1
            bias = 0.1
        else:  # 0.01
            bias = 0.01

        if order_type == OrderType.BUY:
            return price - (price % bias)
        elif order_type == OrderType.SELL:
            return price + (bias - (price % bias))
        else:
            raise APIError

    def _make_authorize_header(self, query_string: bytes) -> Dict[str, str]:
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            "access_key": self.access_key,
            "nonce": str(uuid.uuid4()),
            "query_hash": query_hash,
            "query_hash_alg": "SHA512",
        }
        jwt_token = jwt.encode(payload, self.secret_key).decode("utf-8")
        authorize_token = f"Bearer {jwt_token}"
        return {"Authorization": authorize_token}

    def _post_orders(self, side: str, volume: float, price: float):
        url = f"{self.host}/orders/"
        query_params = dict(
            market=self.market,
            side=side,
            volume=volume,
            price=price,
            ord_type="limit",
        )
        query_string = urlencode(query_params).encode()
        headers = self._make_authorize_header(query_string)
        res = requests.post(url, params=query_params, headers=headers)
        return res.json()

    def _delete_order(self, order_id: str):
        url = f"{self.host}/order/"
        query_params = dict(
            uuid=order_id,
        )
        query_string = urlencode(query_params).encode()
        headers = self._make_authorize_header(query_string)
        res = requests.delete(url, params=query_params, headers=headers)
        return res.json()

    def _get_orders_by_uuids(self, uuids: List[str], states: List[str]):
        url = f"{self.host}/orders/"
        query_params = dict(
            market=self.market,
            limit=100,
        )
        basic_query_string = urlencode(query_params)
        uuids_query_string = None
        if uuids:
            uuids_query_string = "&".join([f"uuids[]={uuid}" for uuid in uuids])
            query_params["uuids[]"] = uuids
        states_query_string = "&".join([f"states[]={state}" for state in states])
        query_params["states[]"] = states
        if uuids_query_string:
            query_string = f"{basic_query_string}&{uuids_query_string}&{states_query_string}".encode()
        else:
            query_string = f"{basic_query_string}&{states_query_string}".encode()
        headers = self._make_authorize_header(query_string)
        res = requests.get(url, params=query_params, headers=headers)
        return res.json()

    def _candles_minutes(self, unit: int, count: int):
        url = f"{self.host}/candles/minutes/{unit}"
        query_params = dict(
            market=self.market,
            count=count,
        )
        res = requests.get(url, params=query_params)
        return res.json()

    def _candles_days(self, count: int):
        url = f"{self.host}/candles/days/"
        query_params = dict(
            market=self.market,
            count=count,
        )
        res = requests.get(url, params=query_params)
        return res.json()

    def _orders_chance(self):
        url = f"{self.host}/orders/chance"
        query_params = dict(market=self.market)
        query_string = urlencode(query_params).encode()
        headers = self._make_authorize_header(query_string)
        res = requests.get(url, params=query_params, headers=headers)
        return res.json()

    def _make_order(self, order: Dict[str, str]) -> Order:
        return Order(
            order_id=order["uuid"],
            type=self.sides[order["side"]],
            status=self.states[order["state"]],
            price=float(order["price"]),
            ordered_volume=float(order["volume"]),
            executed_volume=float(order["executed_volume"]),
            paid_fee=float(order["paid_fee"]),
            ordered_time=datetime.fromisoformat(order["created_at"]),
        )

    def _make_price(self, price: Dict[str, str]) -> Price:
        return Price(
            date_time=datetime.fromisoformat(price["candle_date_time_kst"]),
            high_price=float(price["high_price"]),
            low_price=float(price["low_price"]),
            trade_price=float(price["trade_price"]),
        )


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
