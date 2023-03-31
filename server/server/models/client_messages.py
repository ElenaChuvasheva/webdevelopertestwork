from __future__ import annotations

import decimal
import uuid
from typing import TYPE_CHECKING, TypeVar

import bidict as bidict
import fastapi
import pydantic

from server import enums, message_processors
from server.models.base import Envelope, Message
from server.models.server_messages import ServerMessageT

if TYPE_CHECKING:
    from server.ntpro_server import NTProServer


class ClientEnvelope(Envelope):
    message_type: enums.ClientMessageType

    def get_parsed_message(self):
        return _CLIENT_MESSAGE_TYPE_BY_CLASS.inverse[self.message_type].parse_obj(self.message)


class ClientMessage(Message):
    async def process(self: ClientMessageT,
                      server: NTProServer,
                      websocket: fastapi.WebSocket) -> ServerMessageT:
        return await _MESSAGE_PROCESSOR_BY_CLASS[self.__class__](server, websocket, self)

    def get_type(self: ClientMessageT) -> enums.ClientMessageType:
        return _CLIENT_MESSAGE_TYPE_BY_CLASS[self.__class__]


class SubscribeMarketData(ClientMessage):
    instrument: enums.Instrument


class UnsubscribeMarketData(ClientMessage):
    subscription_id: uuid.UUID


class PlaceOrder(ClientMessage):
    instrument: int
    side: enums.OrderSide
    amount: pydantic.condecimal(gt=decimal.Decimal())
    price: pydantic.condecimal(gt=decimal.Decimal())


class CancelOrder(ClientMessage):
    order_id: uuid.UUID


class GetOrders(ClientMessage):
    pass


class SaveOrder(ClientMessage):
    order_id: uuid.UUID


_MESSAGE_PROCESSOR_BY_CLASS = {
    SubscribeMarketData: message_processors.subscribe_market_data_processor,
    UnsubscribeMarketData: message_processors.unsubscribe_market_data_processor,
    PlaceOrder: message_processors.place_order_processor,
    CancelOrder: message_processors.cancel_order_processor,
    GetOrders: message_processors.get_orders_processor,
}

_CLIENT_MESSAGE_TYPE_BY_CLASS = bidict.bidict({
    SubscribeMarketData: enums.ClientMessageType.subscribe_market_data,
    UnsubscribeMarketData: enums.ClientMessageType.unsubscribe_market_data,
    PlaceOrder: enums.ClientMessageType.place_order,
    CancelOrder: enums.ClientMessageType.cancel_order,
    GetOrders: enums.ClientMessageType.get_orders,
})

ClientMessageT = TypeVar('ClientMessageT', bound=ClientMessage)
