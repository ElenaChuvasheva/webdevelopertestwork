from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import asyncpg
from databases.backends.postgres import Record
from models.dbase import (database, instruments_table, quotes_table,
                          subscribes_table)
from sqlalchemy import asc, select
from utils import dict_from_record, dict_list_from_records

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
            uuid=uuid.uuid4()
        ).returning(subscribes_table.c.uuid)
        subscribe = await database.fetch_one(subscribe_query)
        subscribe_dict = dict_from_record(subscribe)
    except asyncpg.exceptions.UniqueViolationError:
        return server_messages.ErrorInfo(reason='The subscription already exists')

    # context = {'subscriptionId': subscribe_dict.get('uuid').hex}
    return server_messages.SuccessInfo(subscription_id=subscribe_dict.get('uuid').hex)
    # return server_messages.SuccessInfo(info=context)


async def unsubscribe_market_data_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.UnsubscribeMarketData,
):
    from models import server_messages

    uuid = message.dict().get('subscription_id')
    unsubscribe_query = subscribes_table.delete().where(
        subscribes_table.c.uuid == uuid).returning(subscribes_table.c.uuid)
    subscribe = await database.fetch_all(unsubscribe_query)    
    if not subscribe:
        return server_messages.ErrorInfo(reason='The subscription does not exist')            
    # server.connections[websocket.client].subscriptions.append(asyncio.create_task(say_lol(websocket)))
    # context = {'subscriptionId': uuid.hex}
    # return server_messages.SuccessInfo(info=context)
    return server_messages.SuccessInfo(subscription_id=uuid.hex)


async def place_order_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.PlaceOrder,
):
    from models import server_messages

    # TODO ...
    context = {'orderId': uuid.uuid4().hex}
    return server_messages.SuccessInfo(info=context)

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
    
    instrument_id = 2
    inst_query = select(instruments_table).where(instruments_table.c.id == instrument_id)
    instrument = await database.fetch_one(inst_query)
    if instrument is None:
        return server_messages.ErrorInfo(reason=f'Instrument with id={id} does not exist')

    quotes_query = quotes_table.insert().values(
        uuid=uuid.uuid4(),
        instrument=instrument_id,
        timestamp=datetime.now(),
        bid=Decimal('35.00'),
        offer=Decimal('34.50'),
        min_amount=Decimal('33.00'),
        max_amount=Decimal('36.00')
    ).returning(
        quotes_table.c.bid,
        quotes_table.c.offer,
        quotes_table.c.min_amount,
        quotes_table.c.max_amount
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
        await server.send(
            server_messages.MarketDataUpdate(
            subscription_id=subscribes_dict.get('uuid').hex,
            instrument=instrument_id,
            quotes=quotes_list), websocket)
