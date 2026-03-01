from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.core.config import get_settings
from app.db.base import Base

settings = get_settings()

engine = create_async_engine(settings.ASYNC_DATABASE_URL)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

async def get_session():
    async with async_session_maker() as session:
        yield session