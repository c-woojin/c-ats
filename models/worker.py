from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Type, List, Optional, Tuple, Set
from uuid import uuid4

from constants import (
    Exchange,
    Market,
    WorkerStatus,
    DEFAULT_BUDGET,
    OrderStatus,
    PriceUnit,
    OrderType,
    SELL_RATE,
    MIN_ORDER_BUDGET,
    ADDITIONAL_BUY_RATE,
)
from models.exchange_api import (
    AbstractExchangeAPI,
    UpbitExchangeAPI,
    BithumbExchangeAPI,
    CoinoneExchangeAPI,
    FakeExchangeAPI,
    APIError,
)
from models.order import Order
from values import Price


def work(worker: Worker) -> None:
    try:
        if worker.status == WorkerStatus.WATCHING:
            worker.work_for_watching()
        elif worker.status == WorkerStatus.BUYING:
            worker.work_for_buying()
        elif worker.status == WorkerStatus.SELLING:
            worker.work_for_selling()
    except APIError:
        # Todo : Implements API error handling logic
        pass


EXCHANGE_APIS: Dict[str, Type[AbstractExchangeAPI]] = {
    Exchange.UPBIT: UpbitExchangeAPI,
    Exchange.BITHUMB: BithumbExchangeAPI,
    Exchange.COINONE: CoinoneExchangeAPI,
    Exchange.FAKE: FakeExchangeAPI,
}


@dataclass
class Worker:
    market: Market = Market.ETH
    status: WorkerStatus = WorkerStatus.WATCHING
    budget: str = DEFAULT_BUDGET
    orders: Set[Order] = field(default_factory=set)
    balance: float = 0.0
    prices: List[Price] = field(default_factory=list)
    worker_id: str = str(uuid4())
    exchange: Exchange = Exchange.UPBIT

    _api: Optional[AbstractExchangeAPI] = None

    """
    Main methods
    """

    def work_for_watching(self):
        self._update_prices_from_api()
        if self._is_buy_timing():
            api = self._get_api()
            order = api.buy_order(
                price=self._get_trade_price(), budget=self._get_unit_budget()
            )
            self.orders.add(order)
            self.status = WorkerStatus.BUYING

    def work_for_buying(self):
        self._update_orders_from_api()
        self._update_balance_from_api()
        self._update_prices_from_api()
        api = self._get_api()
        latest_order = self._get_latest_order()

        if self._need_to_cancel_buy_order_due_to_trade_price_rising():
            api.cancel_order(latest_order.order_id)
        elif self._need_to_sell_or_buy_order():
            self._spend_budget(
                spent_budget=latest_order.executed_volume * latest_order.price
                + latest_order.paid_fee
            )
            buy_price_average = self._calculate_buy_price_average()
            order = api.sell_order(
                price=buy_price_average * SELL_RATE, volume=self.balance
            )
            self.orders.add(order)
            self.status = WorkerStatus.SELLING
        else:
            self.status = WorkerStatus.WATCHING

    def work_for_selling(self):
        self._update_orders_from_api()
        self._update_balance_from_api()
        self._update_prices_from_api()
        api = self._get_api()
        latest_order = self._get_latest_order()

        if self._need_to_cancel_sell_order_due_to_trade_price_drop():
            api.cancel_order(latest_order.order_id)
        elif self._need_to_sell_or_buy_order():
            order = api.buy_order(
                price=self._get_next_additional_buy_price(),
                budget=self._get_unit_budget(),
            )
            self.orders.add(order)
            self.status = WorkerStatus.BUYING
        else:
            self.status = WorkerStatus.FINISHED

    def _is_buy_timing(self) -> bool:
        price_average = self._calculate_price_average()
        trade_price = self._get_trade_price()
        if price_average and trade_price:
            return True if trade_price < price_average else False
        return False

    def _need_to_cancel_buy_order_due_to_trade_price_rising(self) -> bool:
        latest_order = self._get_latest_order()
        trade_price = self._get_trade_price()
        buy_price_average = self._calculate_buy_price_average()

        if latest_order and trade_price:
            is_buying_status = self.status == WorkerStatus.BUYING
            is_price_rising_for_selling_order = (
                trade_price >= buy_price_average if buy_price_average else False
            )
            is_price_rising_for_returning_watching = trade_price > latest_order.price
            has_balance = self.balance > 0
            can_cancel_order = latest_order.status == OrderStatus.WAIT
            return (
                is_buying_status
                and can_cancel_order
                and (
                    (has_balance and is_price_rising_for_selling_order)
                    or (not has_balance and is_price_rising_for_returning_watching)
                )
            )
        return False

    def _need_to_cancel_sell_order_due_to_trade_price_drop(self) -> bool:
        latest_order = self._get_latest_order()
        latest_buy_order = self._get_latest_order(order_type=OrderType.BUY)
        trade_price = self._get_trade_price()
        next_additional_buy_price = self._get_next_additional_buy_price()

        if (
            latest_order
            and latest_buy_order
            and trade_price
            and next_additional_buy_price
        ):
            is_selling_status = self.status == WorkerStatus.SELLING
            is_price_drop_for_additional_buy = (
                trade_price <= next_additional_buy_price
            )
            has_budget = self._get_unit_budget() > 0
            return (
                is_selling_status and is_price_drop_for_additional_buy and has_budget
            )
        return False

    def _need_to_sell_or_buy_order(self) -> bool:
        latest_order = self._get_latest_order()

        if latest_order:
            is_wait_status_for_latest_order = latest_order == OrderStatus.WAIT
            has_balance = self.balance > 0
            return not is_wait_status_for_latest_order and has_balance
        return False

    """
    Budgets related
    """

    def _get_unit_budget(self) -> int:
        budgets = self.budget.split(":")
        if budgets and budgets[0] and int(budgets[0]) >= MIN_ORDER_BUDGET:
            return int(budgets[0])
        return 0

    def _spend_budget(self, spent_budget: float):
        budgets = self.budget.split(":")
        if int(budgets[0]) - spent_budget > MIN_ORDER_BUDGET:
            budgets[0] = str(int(budgets[0]) - spent_budget)
        else:
            budgets.pop(0)
        self.budget = ":".join(budgets)

    """
    Orders related
    """

    def _update_orders_from_api(self) -> None:
        wait_orders = self._get_orders_by_status(statuses=(OrderStatus.WAIT,))
        if wait_orders:
            api = self._get_api()
            updated_orders = api.get_orders(
                order_ids=[order.order_id for order in wait_orders]
            )
            self.orders.update(set(updated_orders))

    def _get_orders_by_status(self, statuses: Tuple[OrderStatus, ...]) -> List[Order]:
        return [order for order in self.orders if order.status in statuses]

    def _get_orders_by_type(self, types: Tuple[OrderType, ...]) -> List[Order]:
        return [order for order in self.orders if order.type in types]

    def _get_latest_order(
        self, order_type: Optional[OrderType] = None
    ) -> Optional[Order]:
        orders = (
            [order for order in self.orders if order.type == order_type]
            if order_type
            else self.orders
        )
        if orders:
            return max(orders)  # type: ignore
        return None

    def _calculate_buy_price_average(self) -> Optional[float]:
        buy_orders = self._get_orders_by_type(types=(OrderType.BUY,))
        if buy_orders:
            total_funds = sum(
                [
                    order.price * order.executed_volume + order.paid_fee
                    for order in buy_orders
                ]
            )
            return total_funds / len(buy_orders)
        return None

    """
    Balance related
    """

    def _update_balance_from_api(self):
        api = self._get_api()
        self.balance = api.get_balance()

    """
    Prices related
    """

    def _update_prices_from_api(self) -> None:
        api = self._get_api()
        self.prices = api.get_prices(price_unit=PriceUnit.HOUR, counts=24)

    def _get_trade_price(self) -> Optional[float]:
        return max(self.prices).trade_price if self.prices else None  # type: ignore

    def _calculate_price_average(self) -> Optional[float]:
        if self.prices:
            all_price = sum(self.prices[1:], self.prices[0])
            price_sum = (
                all_price.high_price + all_price.low_price + all_price.trade_price
            )
            return price_sum / (3 * len(self.prices))
        return None

    def _get_next_additional_buy_price(self) -> Optional[float]:
        latest_buy_order = self._get_latest_order(order_type=OrderType.BUY)
        return (
            latest_buy_order.price * ADDITIONAL_BUY_RATE if latest_buy_order else None
        )

    """
    api related
    """

    def _get_api(self):
        if self._api:
            return self._api
        self._api = EXCHANGE_APIS[self.exchange](market=self.market)
        return self._api
