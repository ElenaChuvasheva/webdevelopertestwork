import csv
import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine

from server.models.dbase import instruments_table, quotes_table

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, 'server', 'server', 'data')
load_dotenv()

DB_NAME = os.getenv("DB_NAME", "exchange")
DB_USER = os.getenv("DB_USER", "user")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

SYNC_DATABASE_URL = (f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)

def read_file(filename):
    filepath = os.path.join(CSV_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = list(csv.reader(f))
    return reader


def create_object(DBClass, row, engine):
    if DBClass == instruments_table:
        kwargs = {'id': int(row[0]), 'name': row[1]}
    elif DBClass == quotes_table:
        kwargs = {#'uuid': uuid.uuid4(), 
                  'instrument': int(row[1]),
                  'timestamp': datetime.now(), 'bid': row[2],
                  'offer': row[3], 'min_amount': row[4], 'max_amount': row[5]}
    with engine.begin() as conn:
        conn.execute(DBClass.insert(), kwargs)
        # закрывать подключение?
    

def read_to_DB(filename, DBClass, engine):
    reader = read_file(filename)
    for row in reader:
        create_object(DBClass, row, engine)

read_to_DB('instruments.csv', instruments_table, sync_engine)
read_to_DB('quotes.csv', quotes_table, sync_engine)

