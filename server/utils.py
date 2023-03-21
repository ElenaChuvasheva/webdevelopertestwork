import fastapi
from models.dbase import database, subscribes_table


async def delete_users_subscribes(websocket: fastapi.WebSocket):
    query = subscribes_table.delete().where(
        subscribes_table.c.address == str(websocket.client))
    await database.fetch_all(query)
