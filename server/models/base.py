from __future__ import annotations

import abc
import asyncio
import decimal
from typing import TypeVar

import pydantic
from enums import ClientMessageType, ServerMessageType

# порядок следования функций, классов?

def snake_to_camel(snake_str: str) -> str:
    if snake_str == "":
        return snake_str

    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def dict_from_type_to_str(values, Type):
    for key, value in values.items():
        if isinstance(value, Type):
            values[key] = str(values[key])
    return values

def decimal_round(values, digits):
    quantizer = decimal.Decimal('1.' + ''.join(['0' for _ in range(digits)]))
    for key, value in values.items():
        if isinstance(value, decimal.Decimal):
            values[key] = value.quantize(quantizer)
    return values

def decimal_to_str(values, digits):
    values = decimal_round(values, digits)
    return dict_from_type_to_str(values, decimal.Decimal)

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

    class Config(Camel):
        pass

    @pydantic.root_validator
    def decimal_to_str_validator(cls, values):
        return decimal_to_str(values, 2)

MessageT = TypeVar('MessageT', bound=Message)
