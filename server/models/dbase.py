from functools import partial

import databases
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DECIMAL

Base = declarative_base()

ReqColumn = partial(Column, nullable=False)


DATABASE_URL = 'sqlite+aiosqlite://server/sql.db'

database = databases.Database(DATABASE_URL)

class Instrument(Base):
    __tablename__ = 'instruments'
    id = Column(Integer, primary_key=True, index=True)
    name = ReqColumn(String(100), unique=True)
