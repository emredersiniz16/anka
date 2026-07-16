# kovan/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Termux'ta tak-çalıştır olması için lokal aiosqlite kullanıyoruz.
# İleride gerçek sunucuya geçersen buraya PostgreSQL URL'si yazman yeterli.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///kovan_merkez.db")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session
