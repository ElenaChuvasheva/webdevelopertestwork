from server.models.dbase import database, orders_table


async def create_order(websocket, uuid, new_order):
    create_query = orders_table.insert().values(
        uuid=uuid, address=str(websocket.client),
        **new_order.dict()).returning(
        orders_table.c.uuid)
    await database.connect()
    record = await database.fetch_one(create_query)
    await database.disconnect()
    uuid_from_db = dict(zip(record, record._mapping.values())).get('uuid')    
    return uuid_from_db


async def update_order(uuid, order):
    update_query = orders_table.update().where(
        orders_table.c.uuid == uuid).values(
        status=order.dict().get('status'),
        change_time=order.dict().get('change_time')).returning(
        orders_table.c.uuid)
    await database.connect()
    record = await database.execute(update_query)
    await database.disconnect()
    return record
