from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from random import choice, randint, uniform
from typing import TYPE_CHECKING

import asyncpg
from enums import OrderSide, OrderStatus
from models.dbase import (database, instruments_table, orders_table,
                          quotes_table, subscribes_table)
from sqlalchemy import asc, select
from utils import (dict_from_record, dict_list_from_records,
                   fetch_query_one_obj, get_instrument)

if TYPE_CHECKING:
    import fastapi

    from server.models import client_messages
    from server.ntpro_server import NTProServer

async def say_test(websocket: fastapi.WebSocket):
    await websocket.send_text('test')

async def say_lol(websocket: fastapi.WebSocket):
    await websocket.send_text('lol')


async def subscribe_market_data_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.SubscribeMarketData,
):

    from models import server_messages

    id = message.dict().get('instrument')
    inst_query = select(instruments_table).where(instruments_table.c.id == id)
    instrument = await database.fetch_one(inst_query)
    if instrument is None:
        return server_messages.ErrorInfo(reason=f'Instrument with id={id} does not exist')

    try:
        subscribe_query = subscribes_table.insert().values(
            instrument=id,
            address=str(websocket.client),
        ).returning(subscribes_table.c.uuid)
        # subscribe = await database.fetch_one(subscribe_query)
        # subscribe_dict = dict_from_record(subscribe)
        subscribe_dict = await fetch_query_one_obj(subscribe_query)
    except asyncpg.exceptions.UniqueViolationError:
        return server_messages.ErrorInfo(reason='The subscription already exists')

    return server_messages.SuccessInfo(
        subscription_id=subscribe_dict.get('uuid'))


async def unsubscribe_market_data_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.UnsubscribeMarketData,
):
    from models import server_messages

    uuid = message.dict().get('subscription_id')
    unsubscribe_query = subscribes_table.delete().where(
        subscribes_table.c.uuid == uuid).returning(subscribes_table.c.uuid)
    # subscribe = await database.fetch_all(unsubscribe_query) 
    subscribe_dict = await fetch_query_one_obj(unsubscribe_query)

#    if not subscribe:
#        return server_messages.ErrorInfo(reason='The subscription does not exist')            
    # server.connections[websocket.client].subscriptions.append(asyncio.create_task(say_lol(websocket)))
    return server_messages.SuccessInfo(
        subscription_id=subscribe_dict.get('uuid'))


async def place_order_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.PlaceOrder,
):
    from models import server_messages

    instrument_id = await get_instrument(message)

    order_query = orders_table.insert().values(
        instrument=instrument_id,
        side=message.dict().get('side'),
        status=OrderStatus.active,
        amount=message.dict().get('amount'),
        price=message.dict().get('price'),        
        address=str(websocket.client),
        timestamp=datetime.now(),
    ).returning(orders_table.c.uuid)
    order_dict = await fetch_query_one_obj(order_query)
    
    return server_messages.ExecutionReport(order_id=order_dict.get('uuid'),
                                           order_status=OrderStatus.active)

async def cancel_order_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.PlaceOrder,
):
    from models import server_messages
    uuid = message.dict().get('order_id')

    cancel_query = orders_table.update().where(
        orders_table.c.uuid == uuid,
        orders_table.c.status == OrderStatus.active).values(
        status=OrderStatus.cancelled).returning(orders_table.c.uuid)
    cancelled_order_dict = await fetch_query_one_obj(cancel_query)

    return server_messages.ExecutionReport(order_id=cancelled_order_dict.get('uuid'),
                                           order_status=OrderStatus.cancelled)

async def order_magic(
        server: NTProServer,
        websocket: fastapi.WebSocket
):    
    from models import server_messages

    orders_dict_list = await get_orders_dict_list(websocket)
    print(orders_dict_list)
    if not orders_dict_list:
        return
    
    changed_orders_dict = await change_order_random(orders_dict_list)

    await server.send(server_messages.ExecutionReport(
        order_id=changed_orders_dict.get('uuid'),
        order_status=OrderStatus[changed_orders_dict.get('status')]),
        websocket)
    # получаем из бд созданные пользователем активные заявки. нету - валим
    # выбираем одну случайным образом
    # случайным образом выбираем статус filled/rejected

async def change_order_random(orders_dict_list):
    order_to_change = choice(orders_dict_list)
    uuid = order_to_change.get('uuid')    
    new_status = choice([OrderStatus.filled, OrderStatus.rejected])
    change_query = orders_table.update().where(
        orders_table.c.uuid == uuid).values(
        status=new_status).returning(
        orders_table.c.uuid, orders_table.c.status)
    return await fetch_query_one_obj(change_query)
    

# порядок расположения - важен?
async def get_orders_dict_list(websocket: fastapi.WebSocket):
    orders_query = select(orders_table.c.uuid).where(
        orders_table.c.address == str(websocket.client),
        orders_table.c.status == OrderStatus.active)
    orders = await database.fetch_all(orders_query)
    return dict_list_from_records(orders)


async def quote_magic(
        server: NTProServer        
):
    instrument_id = await make_new_quote(server)
    quotes_dict_list, subscribes_dict_list = await get_broadcast_info(
        instrument_id)
    await broadcast_market_data(server, quotes_dict_list,
                                subscribes_dict_list, instrument_id)


async def make_new_quote(
        server: NTProServer
):
    from models import server_messages
    
    instrument_id = randint(1, 3)
    inst_query = select(instruments_table).where(instruments_table.c.id == instrument_id)
    instrument = await database.fetch_one(inst_query)
    if instrument is None:
        return server_messages.ErrorInfo(reason=f'Instrument with id={id} does not exist')

    quote_values = sorted([uniform(30, 40) for _ in range(4)])

    quotes_query = quotes_table.insert().values(
        instrument=instrument_id,
        timestamp=datetime.now(),
        bid=Decimal.from_float(quote_values[1]),
        offer=Decimal.from_float(quote_values[2]),
        min_amount=Decimal.from_float(quote_values[0]),
        max_amount=Decimal.from_float(quote_values[3])
    )    
    await database.fetch_one(quotes_query)
    return instrument_id


async def get_broadcast_info(
        instrument_id: int
):
    quotes_query = select(        
        quotes_table.c.bid,
        quotes_table.c.offer,
        quotes_table.c.min_amount,
        quotes_table.c.max_amount).where(
        quotes_table.c.instrument == instrument_id
        ).order_by(asc(quotes_table.c.timestamp))
    quotes = await database.fetch_all(quotes_query)
    quotes_dict_list = dict_list_from_records(quotes)
    
    subscr_query = select(
        subscribes_table.c.address, subscribes_table.c.uuid).where(
        subscribes_table.c.instrument == instrument_id)
    subscr = await database.fetch_all(subscr_query)
    subscribes_dict_list = dict_list_from_records(subscr)

    return (quotes_dict_list, subscribes_dict_list)


async def broadcast_market_data(server, quotes_dict_list,
                                subscribes_dict_list, instrument_id):
    from models import server_messages
    from models.base import Quote

    quotes_list = [Quote(**x) for x in quotes_dict_list]

    for subscribes_dict in subscribes_dict_list:
        address = subscribes_dict.get('address')
        websocket = server.connections.get(address)
        if websocket is not None:
            await server.send(
                server_messages.MarketDataUpdate(
                subscription_id=subscribes_dict.get('uuid'),
                instrument=instrument_id,
                quotes=quotes_list), websocket)
