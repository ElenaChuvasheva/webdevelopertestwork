import asyncio

import fastapi
import pydantic
import starlette.datastructures

from server.models import base, client_messages, server_messages


class NTProServer:
    def __init__(self):
        self.connections: dict[starlette.datastructures.Address, base.Connection] = {}

    async def connect(self, websocket: fastapi.WebSocket):
        await websocket.accept()
        self.connections[websocket.client] = base.Connection()

    def disconnect(self, websocket: fastapi.WebSocket):
        self.connections.pop(websocket.client)

    # вариант без исключений с таймером?
    # обработка на случай дисконнекта
    async def serve(self, websocket: fastapi.WebSocket):
        while True:
            try:
                raw_envelope = await asyncio.wait_for(websocket.receive_json(), timeout=2)
                envelope = client_messages.ClientEnvelope.parse_obj(raw_envelope)
                message = envelope.get_parsed_message()
                response = await message.process(self, websocket)
                await self.send(response, websocket)
            except asyncio.TimeoutError:
                await websocket.send_text('а что там с котировками?')
            except pydantic.ValidationError as ex:
                await self.send(server_messages.ErrorInfo(reason=str(ex)), websocket)
                continue

    @staticmethod
    async def send(message: base.MessageT, websocket: fastapi.WebSocket):
        await websocket.send_json(server_messages.ServerEnvelope(message_type=message.get_type(),
                                                                 message=message.dict()).dict())
