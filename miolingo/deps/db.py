from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from miolingo.db.session import async_session_factory


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
