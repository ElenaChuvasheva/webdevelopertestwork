from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select

if TYPE_CHECKING:
    import fastapi

    from server.models import client_messages
    from server.ntpro_server import NTProServer


async def subscribe_market_data_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.SubscribeMarketData,
):

    from models import server_messages
    from models.dbase import Instrument, database

#    id = message.dict().get('instrument')
#    inst_query = select(Instrument).where(Instrument.id == id)
#    result = await database.fetch_one(inst_query)
#    if result is None:
#        return server_messages.ErrorInfo(reason=f'Instrument with id={id} does not exist')
    
    context = {'subscriptionId': uuid.uuid4().hex}
    return server_messages.SuccessInfo(info=context)


async def unsubscribe_market_data_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.UnsubscribeMarketData,
):
    from models.server_messages import SuccessInfo

    # TODO ...
    context = {'subscriptionId': message.dict()['subscription_id'].hex}
    return SuccessInfo(info=context)


async def place_order_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.PlaceOrder,
):
    from models import server_messages

    # TODO ...
    context = {'orderId': uuid.uuid4().hex}
    return server_messages.SuccessInfo(info=context)
