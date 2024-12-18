from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from .config import settings

# Create an asynchronous database engine
async_engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# Create a sessionmaker factory for async sessions
async_session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db() -> None:
    """Initialize the database by creating all tables."""
    async with async_engine.begin() as conn:
        # Explicitly running sync methods to ensure tables are created
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for dependency injection."""
    # Using async with to ensure the session is properly closed after use
    async with async_session() as session:
        yield session
