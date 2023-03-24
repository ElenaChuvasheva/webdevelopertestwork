from __future__ import annotations

import abc
import asyncio
import decimal
import uuid
from datetime import datetime
from typing import TypeVar

import pydantic
from enums import ClientMessageType, OrderSide, OrderStatus, ServerMessageType

# порядок следования функций, классов?

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
    def get_parsed_message(self): ...


class Message(pydantic.BaseModel, abc.ABC):
    class Config(Camel):
        frozen = True
        extra = pydantic.Extra.forbid
       
    @abc.abstractmethod
    def get_type(self): ...


class Connection(pydantic.BaseModel):
    class Config:
        arbitrary_types_allowed = True

    subscriptions: list[asyncio.Task] = []


class Quote(pydantic.BaseModel):
    bid: decimal.Decimal
    offer: decimal.Decimal
    min_amount: decimal.Decimal
    max_amount: decimal.Decimal
    timestamp: datetime

    class Config(Camel):
        pass

#    @pydantic.validator('bid', 'offer', 'min_amount', 'max_amount', pre=True)
#    def validate_decimals(cls, value):
#        return str(value.quantize(decimal.Decimal('1.00')))

class Order(pydantic.BaseModel):
    creation_time: datetime
    uuid: uuid.UUID
    change_time: datetime
    status: OrderStatus
    side: OrderSide
    price: decimal.Decimal
    amount: int
    instrument: str

    @pydantic.validator('status', pre=True)
    def validate_status(cls, value):
        return OrderStatus[value]

    @pydantic.validator('side', pre=True)
    def validate_side(cls, value):
        return OrderSide[value]

    class Config(Camel):
        pass

class Instrument(pydantic.BaseModel):
    id: int
    name: str

    class Config(Camel):
        pass

MessageT = TypeVar('MessageT', bound=Message)
