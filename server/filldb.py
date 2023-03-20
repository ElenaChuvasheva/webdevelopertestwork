import csv
import os

from dotenv import load_dotenv
from models.dbase import Instrument
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, 'server', 'data')
load_dotenv()

DB_NAME = os.getenv("DB_NAME", "exchange")
DB_USER = os.getenv("DB_USER", "user")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

SYNC_DATABASE_URL = (f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autoflush=False, bind=sync_engine)
db = SessionLocal()

def read_file(filename):
    filepath = os.path.join(CSV_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = list(csv.reader(f))
    print(reader)
    return reader


def create_object(DBClass, row):
    if DBClass == Instrument:
        kwargs = {'id': int(row[0]), 'name': row[1]}
    db.add(DBClass(**kwargs))

def read_to_DB(filename, DBClass):
    reader = read_file(filename)
    for row in reader:
        create_object(DBClass, row)

read_to_DB('instruments.csv', Instrument)

db.commit()
