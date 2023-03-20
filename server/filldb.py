import csv
import os

from models.dbase import Instrument
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, 'server', 'data')

SYNC_DATABASE_URL = 'sqlite:///./sql.db'
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
