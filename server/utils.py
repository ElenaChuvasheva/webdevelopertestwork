from typing import List

import fastapi
from databases.backends.postgres import Record
from models.dbase import database, instruments_table, subscribes_table
from sqlalchemy import select


async def delete_users_subscribes(websocket: fastapi.WebSocket):
    query = subscribes_table.delete().where(
        subscribes_table.c.address == str(websocket.client))
    await database.fetch_all(query)

def dict_from_record(record: Record):
    return dict(zip(record, record.values()))

def dict_list_from_records(records: List[Record]):
    return [dict(zip(x, x.values())) for x in list(records)]

async def get_instrument(message):
    id = message.dict().get('instrument')
    inst_query = select(instruments_table).where(instruments_table.c.id == id)
    instrument = await database.fetch_one(inst_query)
    if instrument is None:
        raise KeyError(f'Instrument with id={id} does not exist')
    return id

async def fetch_query_one_obj(query):
    object = await database.fetch_one(query)
    if not object:
        raise KeyError(f'Required object does not exist. Query: {query}')
    return dict_from_record(object)