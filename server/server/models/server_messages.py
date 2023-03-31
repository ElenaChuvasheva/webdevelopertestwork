from __future__ import annotations

import uuid
from typing import TypeVar

import bidict as bidict

from server import enums
from server.models.base import Envelope, Message, OrderOut, Quote


class ServerMessage(Message):
    def get_type(self: ServerMessageT) -> enums.ServerMessageType:
        return _SERVER_MESSAGE_TYPE_BY_CLASS[self.__class__]


class ErrorInfo(ServerMessage):
    reason: str


class SuccessInfo(ServerMessage):
    subscription_id: uuid.UUID


class ExecutionReport(ServerMessage):
    order_id: uuid.UUID
    order_status: enums.OrderStatus


class MarketDataUpdate(ServerMessage):
    subscription_id: uuid.UUID
    instrument: enums.Instrument
    quotes: list[Quote]


class OrdersList(ServerMessage):
    orders: list[OrderOut]


class ServerEnvelope(Envelope):
    message_type: enums.ServerMessageType

    def get_parsed_message(self):
        return _SERVER_MESSAGE_TYPE_BY_CLASS.inverse[self.message_type].parse_obj(self.message)

    class Config(Envelope.Config):
        json_encoders = {
            enums.Instrument: lambda e: e.name.replace('_', '/').upper(),
            enums.OrderSide: lambda e: e.name,
            enums.OrderStatus: lambda e: e.name}


_SERVER_MESSAGE_TYPE_BY_CLASS = bidict.bidict({
    SuccessInfo: enums.ServerMessageType.success,
    ErrorInfo: enums.ServerMessageType.error,
    ExecutionReport: enums.ServerMessageType.execution_report,
    MarketDataUpdate: enums.ServerMessageType.market_data_update,
    OrdersList: enums.ServerMessageType.orders_list,
})
ServerMessageT = TypeVar('ServerMessageT', bound=ServerMessage)
