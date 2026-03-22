from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

#No idea what this does
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True) # The actual connection to the db, echo js means print commands

AsyncSessionLocal = async_sessionmaker( # The method that makes a session (Temp workspace) that we use to type out sql commands. async_sessionmaker is the factory that makes the sessions
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base() # The basw class all models derivce from
