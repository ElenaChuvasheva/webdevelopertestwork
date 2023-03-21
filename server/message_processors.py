from __future__ import annotations

import asyncio
import uuid
from typing import TYPE_CHECKING

import asyncpg
from models.dbase import database, instruments_table, subscribes_table
from sqlalchemy import select

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
        subscribe_dict = dict(zip(subscribe.keys(), subscribe.values()))
        server.connections[websocket.client].subscriptions.append(asyncio.create_task(say_test(websocket)))
    except asyncpg.exceptions.UniqueViolationError:
        return server_messages.ErrorInfo(reason='The subscription already exists')

    context = {'subscriptionId': subscribe_dict['uuid'].hex}
    return server_messages.SuccessInfo(info=context)


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
    server.connections[websocket.client].subscriptions.append(asyncio.create_task(say_lol(websocket)))
    context = {'subscriptionId': uuid.hex}
    return server_messages.SuccessInfo(info=context)


async def place_order_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.PlaceOrder,
):
    from models import server_messages

    # TODO ...
    context = {'orderId': uuid.uuid4().hex}
    return server_messages.SuccessInfo(info=context)
