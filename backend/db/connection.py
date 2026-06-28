from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import env


class Base(DeclarativeBase):
    """Base class for ORM mapped classes (entities)."""


engine = create_async_engine(
    env.DATABASE_URL, echo=False, pool_size=10, max_overflow=20
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """One AsyncSession per request; closed after the request."""
    async with AsyncSessionLocal() as session:
        yield session
