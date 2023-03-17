from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import fastapi

    from server.models import client_messages
    from server.ntpro_server import NTProServer


async def subscribe_market_data_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.SubscribeMarketData,
):

    from server.models import server_messages

    # TODO ...
    context = {'subscriptionId': uuid.uuid4().hex}
    return server_messages.SuccessInfo(info=context)


async def unsubscribe_market_data_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.UnsubscribeMarketData,
):
    from server.models.server_messages import SuccessInfo

    # TODO ...
    context = {'subscriptionId': message.dict()['subscription_id'].hex}
    return SuccessInfo(info=context)


async def place_order_processor(
        server: NTProServer,
        websocket: fastapi.WebSocket,
        message: client_messages.PlaceOrder,
):
    from server.models import server_messages

    # TODO ...

    context = {'orderId': uuid.uuid4().hex}
    return server_messages.SuccessInfo(info=context)
