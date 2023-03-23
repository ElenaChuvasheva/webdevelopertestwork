import os
from functools import partial

import databases
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.types import DECIMAL

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "exchange")
DB_USER = os.getenv("DB_USER", "user")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

SQLALCHEMY_DATABASE_URL = (f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
database = databases.Database(SQLALCHEMY_DATABASE_URL)

ReqColumn = partial(Column, nullable=False)

metadata = sqlalchemy.MetaData()

instruments_table = sqlalchemy.Table(
    'instruments',
    metadata,
    Column('id', Integer, primary_key=True),
    ReqColumn('name', String, unique=True),
)

quotes_table = sqlalchemy.Table(
    'quotes',
    metadata,
    Column('uuid', UUID(as_uuid=True), primary_key=True,
           server_default=sqlalchemy.text("uuid_generate_v4()")),
    ReqColumn('instrument', ForeignKey(instruments_table.c.id,
                                       onupdate="CASCADE",
                                       ondelete="CASCADE")),
    ReqColumn('timestamp', DateTime()),
    # ReqColumn('instrument', ENUM(Instrument), unique=True, index=True),
    ReqColumn('bid', DECIMAL),
    ReqColumn('offer', DECIMAL),
    ReqColumn('min_amount', DECIMAL),
    ReqColumn('max_amount', DECIMAL)
)

subscribes_table = sqlalchemy.Table(
    'subscribes',
    metadata,
    Column('uuid', UUID(as_uuid=True), primary_key=True,
           server_default=sqlalchemy.text("uuid_generate_v4()")),
    ReqColumn('instrument', ForeignKey(instruments_table.c.id,
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                                       index=True),
    ReqColumn('address', String),
    UniqueConstraint('instrument', 'address', name='instrument_address_constraint')
)
