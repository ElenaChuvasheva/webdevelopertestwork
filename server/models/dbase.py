from functools import partial

import databases
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DECIMAL

Base = declarative_base()

ReqColumn = partial(Column, nullable=False)


DATABASE_URL = 'sqlite+aiosqlite:///./sql.db'

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
database = databases.Database(DATABASE_URL)

class Instrument(Base):
    __tablename__ = 'instruments'
    id = Column(Integer, primary_key=True, index=True)
    instrument = ReqColumn(String(100), unique=True)
