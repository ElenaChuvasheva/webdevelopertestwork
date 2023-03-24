from __future__ import annotations

import enum


class ClientMessageType(enum.IntEnum):
    subscribe_market_data = enum.auto()
    unsubscribe_market_data = enum.auto()
    place_order = enum.auto()
    cancel_order = enum.auto()
    get_orders = enum.auto()
    get_instruments = enum.auto()


class ServerMessageType(enum.IntEnum):
    success = enum.auto()
    error = enum.auto()
    execution_report = enum.auto()
    market_data_update = enum.auto()
    orders_list = enum.auto()
    instruments_list = enum.auto()


class OrderSide(enum.Enum):
    buy = enum.auto()
    sell = enum.auto()


class OrderStatus(enum.Enum):
    active = enum.auto()
    filled = enum.auto()
    rejected = enum.auto()
    cancelled = enum.auto()


# @enum.unique
# class Instrument(str, enum.Enum):
#    eur_usd = 'EUR/USD'
#    eur_rub = 'EUR/RUB'
#    usd_rub = 'USD/RUB'
