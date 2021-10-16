from dataclasses import dataclass, field
from typing import Dict, Type, List, Optional
from uuid import uuid4

from constants import Exchange, Market, WorkerStatus, DEFAULT_BUDGET
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
    orders: List[Order] = field(default_factory=list)
    balance: float = 0.0
    prices: List[Price] = field(default_factory=list)
    worker_id: str = str(uuid4())
    exchange: Exchange = Exchange.UPBIT

    def is_buy_timing(self) -> bool:
        price_average = self.calculate_price_average()
        trade_price = self.get_trade_price()
        return True if trade_price < price_average else False

    def calculate_price_average(self) -> Optional[float]:
        if self.prices:
            all_price = sum(self.prices[1:], self.prices[0])
            price_sum = all_price.high_price + all_price.low_price + all_price.trade_price
            return price_sum / (3 * len(self.prices))
        return None

    def get_trade_price(self) -> Optional[float]:
        return max(self.prices).trade_price if self.prices else None

    def get_unit_budget(self) -> int:
        budgets = self.budget.split(":")
        if budgets and budgets[0]:
            return int(budgets[0])
        return 0

    def work_for_watching(self):
        if self.is_buy_timing():
            api = EXCHANGE_APIS[self.exchange](market=self.market)
            order = api.buy_order(
                price=self.get_trade_price(), budget=self.get_unit_budget()
            )
            self.orders.append(order)
            self.status = WorkerStatus.BUYING