from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from random import choice, randint, uniform
from typing import TYPE_CHECKING
from uuid import uuid4

from bidict import ValueDuplicationError, bidict
from sqlalchemy import asc, select

from server.enums import Instrument, OrderSide, OrderStatus
from server.models import server_messages
from server.models.base import OrderIn, OrderOut, Quote
from server.models.dbase import database, orders_table

if TYPE_CHECKING:
    import fastapi

    from server.models import client_messages
    from server.ntpro_server import NTProServer

# async def say_test(websocket: fastapi.WebSocket):
#    await websocket.send_text('test')

# async def say_lol(websocket: fastapi.WebSocket):
#    await websocket.send_text('lol')


async def subscribe_market_data_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.SubscribeMarketData,
):
    instrument = message.dict().get('instrument')
    uuid=uuid4()
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
    return server_messages.ExecutionReport(order_id=uuid,
                                           order_status=new_order.status)

async def cancel_order_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.PlaceOrder,
):
    uuid = message.dict().get('order_id')
    order = server.orders[websocket.client].get(uuid)
    if order.status == OrderStatus.active:
        order.status = OrderStatus.cancelled
    return server_messages.ExecutionReport(
        order_id=uuid, order_status=order.status)

async def get_orders_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.PlaceOrder,
):
#    orders_list = server.orders[websocket.client].values()
#    for x in orders_list:
#        print(x.dict())
#    orders_list = server.orders[websocket.client].values()
    orders_list = [OrderOut(
        uuid=uuid, **values.dict()
        ) for uuid, values in server.orders[websocket.client].items()]
#    return server_messages.ErrorInfo(reason='lol')
    # return server_messages.OrdersList(orders=server.orders[websocket.client].values())
    return server_messages.OrdersList(orders=orders_list)

async def save_order_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.SaveOrder,
):
    uuid = message.dict().get('order_id')
    order = server.orders[websocket.client].get(uuid)
    order_query = orders_table.insert().values(
        uuid=uuid, address=str(websocket.client), **order.dict()).returning(
        orders_table.c.uuid)
    
    await database.connect()
    record = await database.fetch_one(order_query)
    uuid_from_db = dict(zip(record, record.values())).get('uuid')
    await database.disconnect()
    return server_messages.OrderSaved(order_id=uuid_from_db)


'''        quotes_query = quotes_table.insert().values(
        instrument=instrument_id,
        timestamp=datetime.now(),
        bid=Decimal.from_float(quote_values[1]),
        offer=Decimal.from_float(quote_values[2]),
        min_amount=Decimal.from_float(quote_values[0]),
        max_amount=Decimal.from_float(quote_values[3])
    )    
    await database.fetch_one(quotes_query)'''

async def order_magic(
        server: NTProServer,
        websocket: fastapi.WebSocket
):
    orders = server.orders[websocket.client]
    active_orders_keys = [key for key, value in orders.items() if value.status == OrderStatus.active]
    if not active_orders_keys:
        return
    key_change = choice(active_orders_keys)
    order_change = orders[key_change]
    # print(order_change)
    order_change.status = choice(
        [OrderStatus.filled, OrderStatus.rejected])
    await server.send(server_messages.ExecutionReport(
        order_id=key_change,
        order_status=order_change.status), websocket)
    
    '''
    from server.models import server_messages

    orders_query = select(orders_table.c.uuid).where(
        orders_table.c.address == str(websocket.client),
        orders_table.c.status == OrderStatus.active)
    orders_dict_list = dict_list_from_records(
        await database.fetch_all(orders_query))
    if not orders_dict_list:
        return
    changed_orders_dict = await change_order_random(orders_dict_list)
    await server.send(server_messages.ExecutionReport(
        order_id=changed_orders_dict.get('uuid'),
        order_status=OrderStatus[changed_orders_dict.get('status')]),
        websocket)
'''

'''async def change_order_random(orders_dict_list):
    order_to_change = choice(orders_dict_list)
    uuid = order_to_change.get('uuid')
    new_status = choice([OrderStatus.filled, OrderStatus.rejected])
    change_query = orders_table.update().where(
        orders_table.c.uuid == uuid).values(
        status=new_status, change_time=datetime.now()).returning(
        orders_table.c.uuid, orders_table.c.status)
    return await fetch_query_one_obj(change_query)
'''

async def quote_magic(
        server: NTProServer        
):
    instrument = choice(list(Instrument))
    quote_values = sorted([uniform(30, 40) for _ in range(4)])
    server.quotes[instrument].append(Quote(
        bid=Decimal.from_float(quote_values[1]),
        offer=Decimal.from_float(quote_values[2]),
        min_amount=Decimal.from_float(quote_values[0]),
        max_amount=Decimal.from_float(quote_values[3])))
    # print(server.quotes)
    for client, client_subscribes in server.subscribes.items():
        # print(client_subscribes.values(), instrument.value)
        # print(instrument in client_subscribes.values())
        if instrument in client_subscribes.values():
            websocket = server.connections.get(client)
            await server.send(
                server_messages.MarketDataUpdate(
                subscription_id=client_subscribes.inverse.get(instrument),
                instrument=instrument,
                quotes=server.quotes[instrument]), websocket)

    '''
    instrument_id = await make_new_quote(server)
    quotes_dict_list, subscribes_dict_list = await get_broadcast_info(
        instrument_id)
    await broadcast_market_data(server, quotes_dict_list,
                                subscribes_dict_list, instrument_id)

async def make_new_quote(
        server: NTProServer
):
    instrument_id = randint(1, 3)
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
        quotes_table.c.max_amount,
        quotes_table.c.timestamp).where(
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
    from server.models import server_messages
    from server.models.base import Quote

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
'''