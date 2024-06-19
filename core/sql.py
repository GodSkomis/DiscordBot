from typing import Any, AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import SQLALCHEMY_DATABASE_URL


Base = declarative_base()


class DatabaseSessionManager:
    _engine = None
    _sessionmaker = None

    @classmethod
    def get_engine(cls):
        return cls._engine
    
    @classmethod
    def setup(cls, db_path: str = None):
        db_path = db_path if db_path else SQLALCHEMY_DATABASE_URL
        cls._engine = create_async_engine(db_path, echo=False, connect_args={"check_same_thread": False})
        cls._sessionmaker = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=cls._engine)

    @classmethod
    async def close(cls):
        if cls._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await cls._engine.dispose()

        cls._engine = None
        cls._sessionmaker = None

    @classmethod
    @asynccontextmanager
    async def connect(cls) -> AsyncIterator[AsyncConnection]:
        if cls._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with cls._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @classmethod
    @asynccontextmanager
    async def session(cls) -> AsyncIterator[AsyncSession]:
        if cls._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = cls._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# DatabaseSessionManager.setup()


# @asynccontextmanager
async def get_db_session() -> AsyncSession:
    async with DatabaseSessionManager.session() as session:
        yield session


async def init_models():
    async with DatabaseSessionManager.get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
