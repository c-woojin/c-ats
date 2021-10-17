from dataclasses import dataclass, field
from typing import Dict, Type, List, Optional, Tuple, Set
from uuid import uuid4

from constants import Exchange, Market, WorkerStatus, DEFAULT_BUDGET, OrderStatus
from exchange_api import AbstractExchangeAPI, UpbitExchangeAPI, BithumbExchangeAPI, \
    CoinoneExchangeAPI, FakeExchangeAPI
from models.order import Order
from values import Price

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

    # Main methods
    def work_for_watching(self):
        if self.is_buy_timing():
            api = self.get_api()
            order = api.buy_order(
                price=self.get_trade_price(), budget=self.get_unit_budget()
            )
            self.orders.add(order)
            self.status = WorkerStatus.BUYING

    def is_buy_timing(self) -> bool:
        price_average = self.calculate_price_average()
        trade_price = self.get_trade_price()
        return True if trade_price < price_average else False

    # Budgets related
    def get_unit_budget(self) -> int:
        budgets = self.budget.split(":")
        if budgets and budgets[0]:
            return int(budgets[0])
        return 0

    # Orders related
    def update_orders_from_api(self) -> None:
        wait_orders = self.get_orders_by_status(statuses=(OrderStatus.WAIT,))
        if wait_orders:
            api = self.get_api()
            updated_orders = api.get_orders(order_ids=[order.order_id for order in wait_orders])
            self.orders.update(set(updated_orders))

    def get_orders_by_status(self, statuses: Tuple[OrderStatus, ...]) -> List[Order]:
        return [order for order in self.orders if order.status in statuses]

    # Balance related

    # Prices related
    def get_trade_price(self) -> Optional[float]:
        return max(self.prices).trade_price if self.prices else None

    def calculate_price_average(self) -> Optional[float]:
        if self.prices:
            all_price = sum(self.prices[1:], self.prices[0])
            price_sum = all_price.high_price + all_price.low_price + all_price.trade_price
            return price_sum / (3 * len(self.prices))
        return None

    # api related
    def get_api(self):
        if self._api:
            return self._api
        self._api = EXCHANGE_APIS[self.exchange](market=self.market)
        return self._api
