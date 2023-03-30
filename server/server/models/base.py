from __future__ import annotations

import abc
import asyncio
import datetime
import decimal
import uuid
from typing import TypeVar

import pydantic

from server.enums import (ClientMessageType, Instrument, OrderSide,
                          OrderStatus, ServerMessageType)


def snake_to_camel(snake_str: str) -> str:
    if snake_str == "":
        return snake_str

    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class Camel:
    alias_generator = snake_to_camel
    allow_population_by_field_name = True


class Envelope(pydantic.BaseModel, abc.ABC):
    class Config(Camel):
        extra = pydantic.Extra.forbid

    message_type: ClientMessageType | ServerMessageType
    message: dict

    @abc.abstractmethod
    def get_parsed_message(self):
        ...


class Message(pydantic.BaseModel, abc.ABC):
    class Config(Camel):
        frozen = True
        extra = pydantic.Extra.forbid

    @abc.abstractmethod
    def get_type(self):
        ...


class Connection(pydantic.BaseModel):
    class Config:
        arbitrary_types_allowed = True

    subscriptions: list[asyncio.Task] = []


class Quote(pydantic.BaseModel):
    bid: decimal.Decimal
    offer: decimal.Decimal
    min_amount: decimal.Decimal
    max_amount: decimal.Decimal
    timestamp: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now)

    class Config(Camel):
        pass


class OrderIn(pydantic.BaseModel):
    creation_time: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now)
    change_time: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now)
    status: OrderStatus = OrderStatus.active
    side: OrderSide
    price: decimal.Decimal
    amount: int
    instrument: Instrument


class OrderOut(OrderIn):
    uuid: uuid.UUID

    class Config(Camel):
        pass


MessageT = TypeVar('MessageT', bound=Message)
