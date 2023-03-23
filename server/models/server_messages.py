from __future__ import annotations

import uuid
from typing import Dict, TypeVar

import bidict as bidict
import enums
from models.base import Envelope, Message, Quote, dict_from_type_to_str
from pydantic import root_validator


class ServerMessage(Message):
    def get_type(self: ServerMessageT) -> enums.ServerMessageType:
        return _SERVER_MESSAGE_TYPE_BY_CLASS[self.__class__]
    
    @root_validator
    def uuid_to_str(cls, values):
        return dict_from_type_to_str(values, uuid.UUID)

    
class ErrorInfo(ServerMessage):
    reason: str

class SuccessInfo(ServerMessage):
    subscription_id: uuid.UUID


class ExecutionReport(ServerMessage):
    order_id: uuid.UUID
    order_status: enums.OrderStatus


class MarketDataUpdate(ServerMessage):
    subscription_id: uuid.UUID
    instrument: int
    quotes: list[Quote]


class ServerEnvelope(Envelope):
    message_type: enums.ServerMessageType

    def get_parsed_message(self):
        return _SERVER_MESSAGE_TYPE_BY_CLASS.inverse[self.message_type].parse_obj(self.message)


_SERVER_MESSAGE_TYPE_BY_CLASS = bidict.bidict({
    SuccessInfo: enums.ServerMessageType.success,
    ErrorInfo: enums.ServerMessageType.error,
    ExecutionReport: enums.ServerMessageType.execution_report,
    MarketDataUpdate: enums.ServerMessageType.market_data_update,
})
ServerMessageT = TypeVar('ServerMessageT', bound=ServerMessage)
