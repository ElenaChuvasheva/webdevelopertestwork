import databases
from fastapi.testclient import TestClient
from sqlalchemy import text

from server.app import api

'''
СЦЕНАРИИ ТЕСТОВ

Общее:
Послал хз что - получил ответ, что это не нормальный JSON

Подписки
Подписался - получил правильный ответ
Пытаешься подписаться на несуществующий инструмент - соотв. сообщение
Пытаешься подписаться на то, на что уже подписан - соотв. сообщение
Отписываешься от существующей подписки - ок
Отписываешься от несуществующей подписки - соотв. сообщение
'''

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test_dbase")
DB_NAME = os.getenv("TEST_DB_NAME", "exchange")
DB_USER = os.getenv("DB_USER", "user")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

SYNC_DATABASE_URL = (f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}")
test_database = databases.Database(SYNC_DATABASE_URL)

@api.on_event('startup')
async def startup():
    await test_database.connect()

@api.on_event('shutdown')
async def shutdown():
    await test_database.disconnect()

@api.get("/")
async def read_main():
    return {"msg": "Hello World"}

sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)

with sync_engine.connect() as conn:
    query = ('CREATE TABLE IF NOT EXISTS public.instruments('
             r" id integer NOT NULL,"
             ' name character varying COLLATE pg_catalog."default" NOT NULL,'
             " CONSTRAINT instruments_pkey PRIMARY KEY (id),"
             " CONSTRAINT instruments_name_key UNIQUE (name))"
             " TABLESPACE pg_default;"
             " ALTER TABLE IF EXISTS public.instruments"
             " OWNER to postgres;")
    conn.execute(text(query))


def test_read_main():
    client = TestClient(api)
    response = client.get("/")
    assert response.status_code == 200


def test_get_instruments():
    client = TestClient(api)
    with client.websocket_connect("/ws/") as websocket:
        websocket.send_text('lol')
#        websocket.send_text('{"messageType": 6, "message": {}}')
#        data = websocket.receive_text()
#        assert websocket == 1
