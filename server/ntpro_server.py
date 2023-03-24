import asyncio
import json
import time
from random import randrange

import fastapi
import pydantic
from message_processors import order_magic, quote_magic
from models import base, client_messages, server_messages
from utils import delete_users_subscribes


class NTProServer:
    def __init__(self):
        self.connections: dict[str, fastapi.WebSocket] = {}
        
    async def connect(self, websocket: fastapi.WebSocket):
        await websocket.accept()
        self.connections[str(websocket.client)] = websocket

    async def disconnect(self, websocket: fastapi.WebSocket):
        await delete_users_subscribes(websocket)
        self.connections.pop(str(websocket.client))

    # вариант без исключений с таймером?
    # рандом по времени изменения котировок, по значениям
    async def serve(self, websocket: fastapi.WebSocket):
        while True:
            try:
                raw_envelope = await asyncio.wait_for(websocket.receive_json(), timeout=10)
                envelope = client_messages.ClientEnvelope.parse_obj(raw_envelope)
                message = envelope.get_parsed_message()
                response = await message.process(self, websocket)
                await self.send(response, websocket)
            except asyncio.TimeoutError:
                #if randrange(0, 1000) %5 == 0:
                await quote_magic(self)
                #if randrange(0, 1000) % 5 == 0:
                await order_magic(self, websocket)
                await websocket.send_text(str(websocket.client))
            except pydantic.ValidationError as ex:
                await self.send(server_messages.ErrorInfo(reason=str(ex)), websocket)
            except json.decoder.JSONDecodeError:
                await self.send(server_messages.ErrorInfo(
                    reason='The message is not a valid JSON'), websocket)
            except Exception as ex:
                await self.send(server_messages.ErrorInfo(reason=str(ex)), websocket)
                continue

    @staticmethod
    async def send(message: base.MessageT, websocket: fastapi.WebSocket):
#        print(server_messages.ServerEnvelope(message_type=message.get_type(),
#                                                                 message=message.dict(by_alias=True)))
        await websocket.send_text(server_messages.ServerEnvelope(message_type=message.get_type(),
                                                                 message=message.dict(by_alias=True)).json(by_alias=True))
