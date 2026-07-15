# kovan/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL URL'n (Burayı kendi sunucuna göre güncelleyeceksin)
DATABASE_URL = "postgresql+asyncpg://admin:sifre@localhost/kovan_db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session
