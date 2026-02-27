from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
# from sqlalchemy import text

from app.core.config import get_settings
from app.db.base import Base

settings = get_settings()

engine = create_async_engine(settings.ASYNC_DATABASE_URL)

async_sessionmaker = async_sessionmaker(engine, class_=AsyncSession)

async def get_session():
    async with async_sessionmaker as session:
        yield session

# def check_con():
#     try:
#         db: AsyncSession = get_session()
#         db.execute(text("SELECT 1"))
#         print("db con")
#         return True
#     except:
#         print("fail")
#         return False
    
# check_con()