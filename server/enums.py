from __future__ import annotations

import enum


class ClientMessageType(enum.IntEnum):
    subscribe_market_data = enum.auto()
    unsubscribe_market_data = enum.auto()
    place_order = enum.auto()


class ServerMessageType(enum.IntEnum):
    success = enum.auto()
    error = enum.auto()
    execution_report = enum.auto()
    market_data_update = enum.auto()


class OrderSide(enum.IntEnum):
    buy = enum.auto()
    sell = enum.auto()


class OrderStatus(enum.IntEnum):
    active = enum.auto()
    filled = enum.auto()
    rejected = enum.auto()
    cancelled = enum.auto()


class Instrument(str, enum.Enum):
    eur_usd = 'EUR/USD'
    eur_rub = 'EUR/RUB'
    usd_rub = 'USD/RUB'
