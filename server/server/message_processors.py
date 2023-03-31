from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from random import choice, uniform
from typing import TYPE_CHECKING
from uuid import uuid4

import asyncpg
from bidict import ValueDuplicationError

from server.enums import Instrument, OrderStatus
from server.models import server_messages
from server.models.base import OrderIn, OrderOut, Quote
from server.models.dbase import database, orders_table
from server.pytest_conditions import RUN_FROM_PYTEST
from server.utils import create_order, update_order


def instrument_condition():
    return Instrument.eur_usd if RUN_FROM_PYTEST else choice(list(Instrument))


if TYPE_CHECKING:
    import fastapi

    from server.models import client_messages
    from server.ntpro_server import NTProServer


async def subscribe_market_data_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.SubscribeMarketData,
):
    instrument = message.dict().get('instrument')
    uuid = uuid4()
    try:
        server.subscribes[websocket.client].update({uuid: instrument})
    except ValueDuplicationError:
        return server_messages.ErrorInfo(reason='The subscribe already exists')
    return server_messages.SuccessInfo(subscription_id=uuid)


async def unsubscribe_market_data_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.UnsubscribeMarketData,
):
    uuid = message.dict().get('subscription_id')
    try:
        server.subscribes[websocket.client].pop(uuid)
    except KeyError:
        return server_messages.ErrorInfo(reason='The subscribe does not exist')
    return server_messages.SuccessInfo(subscription_id=uuid)


async def place_order_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.PlaceOrder,
):
    new_order = OrderIn(**message.dict())
    uuid = uuid4()
    server.orders[websocket.client][uuid] = new_order
    uuid_from_db = await create_order(websocket, uuid, new_order)
    return server_messages.ExecutionReport(order_id=uuid_from_db,
                                           order_status=new_order.status)


async def cancel_order_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.PlaceOrder,
):
    uuid = message.dict().get('order_id')
    try:
        order = server.orders[websocket.client].get(uuid)
        if order.status == OrderStatus.active:
            order.status = OrderStatus.cancelled
            order.change_time = datetime.now()
            uuid_from_db = await update_order(uuid, order)
        else:
            return server_messages.ErrorInfo(
                reason=f'The order is {order.status.name}')
        return server_messages.ExecutionReport(
            order_id=uuid_from_db, order_status=order.status)
    except AttributeError:
        return server_messages.ErrorInfo(reason='The order does not exist')


async def get_orders_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.PlaceOrder,
):
    orders_list = [OrderOut(
        uuid=uuid, **values.dict()
    ) for uuid, values in server.orders[websocket.client].items()]
    return server_messages.OrdersList(orders=orders_list)


async def order_magic(
        server: NTProServer,
        websocket: fastapi.WebSocket
):
    orders = server.orders[websocket.client]
    active_orders_keys = [key for key, value
                          in orders.items()
                          if value.status == OrderStatus.active]
    if not active_orders_keys:
        return
    key_change = choice(active_orders_keys)
    order_change = orders[key_change]
    order_change.status = choice(
        [OrderStatus.filled, OrderStatus.rejected])
    order_change.change_time = datetime.now()
    uuid_from_db = await update_order(key_change, order_change)
    await server.send(server_messages.ExecutionReport(
        order_id=uuid_from_db,
        order_status=order_change.status), websocket)


async def quote_magic(
        server: NTProServer
):
    instrument = instrument_condition()
    quote_values = sorted([uniform(30, 40) for _ in range(4)])
    server.quotes[instrument].append(Quote(
        bid=Decimal.from_float(quote_values[1]),
        offer=Decimal.from_float(quote_values[2]),
        min_amount=Decimal.from_float(quote_values[0]),
        max_amount=Decimal.from_float(quote_values[3])))
    for client, client_subscribes in server.subscribes.items():
        if instrument in client_subscribes.values():
            websocket = server.connections.get(client)
            await server.send(
                server_messages.MarketDataUpdate(
                    subscription_id=client_subscribes.inverse.get(instrument),
                    instrument=instrument, quotes=server.quotes[instrument]),
                websocket)
