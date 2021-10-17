from enum import IntEnum, Enum

DEFAULT_BUDGET = "10000:20000:30000"


class WorkerStatus(IntEnum):
    WATCHING = 1
    BUYING = 2
    SELLING = 3
    FINISHED = 4


class Exchange(str, Enum):
    UPBIT = "UPBIT"
    BITHUMB = "BITHUMB"
    COINONE = "COINONE"
    FAKE = "FAKE"


class Market(str, Enum):
    BTC = "BTC"
    EOS = "EOS"
    ETH = "ETH"


class PriceUnit(IntEnum):
    MINUTE = 1
    HOUR = 2
    DAY = 3


class OrderType(IntEnum):
    BUY = 1
    SELL = 2


class OrderStatus(IntEnum):
    WAIT = 1
    DONE = 2
    CANCEL = 3
