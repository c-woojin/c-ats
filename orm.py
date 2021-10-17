from sqlalchemy import MetaData, Table, Column, String, SmallInteger, Float, DateTime, \
    Integer, ForeignKey
from sqlalchemy.orm import mapper, relationship

from models.order import Order
from models.worker import Worker
from values import Price

metadata = MetaData()

orders = Table(
    "orders",
    metadata,
    Column("order_id", String(255), primary_key=True),
    Column("type", SmallInteger, nullable=False),
    Column("status", SmallInteger, nullable=False),
    Column("price", Float, nullable=False),
    Column("ordered_volume", Float, nullable=False),
    Column("executed_volume", Float, nullable=False),
    Column("paid_fee", Float, nullable=False),
    Column("ordered_time", DateTime, nullable=False),
)

prices = Table(
    "prices",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("date_time", DateTime),
    Column("high_price", Float),
    Column("low_price", Float),
    Column("trade_price", Float),
)

workers = Table(
    "workers",
    metadata,
    Column("worker_id", String(50), primary_key=True),
    Column("market", String(10), nullable=False),
    Column("status", SmallInteger, nullable=False),
    Column("budget", String(100)),
    Column("exchange", String(20)),
)

order_list = Table(
    "order_list",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("order_id", ForeignKey("orders.order_id")),
    Column("worker_id", ForeignKey("workers.worker_id")),
)

price_list = Table(
    "price_list",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("price_id", ForeignKey("prices.id")),
    Column("worker_id", ForeignKey("workers.worker_id")),
)


def start_mappers():
    orders_mapper = mapper(Order, orders)
    prices_mapper = mapper(Price, prices)
    mapper(
        Worker,
        workers,
        properties={
            "orders": relationship(
                orders_mapper, secondary=order_list, collection_class=set,
            ),
            "prices": relationship(
                prices_mapper, secondary=price_list, collection_class=list,
            )
        },
    )
