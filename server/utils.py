from typing import List

import fastapi
from databases.backends.postgres import Record
from models.dbase import database, subscribes_table


async def delete_users_subscribes(websocket: fastapi.WebSocket):
    query = subscribes_table.delete().where(
        subscribes_table.c.address == str(websocket.client))
    await database.fetch_all(query)

def dict_from_record(record: Record):
    return dict(zip(record, record.values()))

def dict_list_from_records(records: List[Record]):
    return [dict(zip(x, x.values())) for x in list(records)]
