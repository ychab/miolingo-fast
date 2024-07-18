from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from miolingo import settings

if settings.POSTGRES_URI_ASYNC is None:  # pragma: no cover
    raise RuntimeError("Did you forgot to export database env vars?")

async_engine: AsyncEngine = create_async_engine(url=str(settings.POSTGRES_URI_ASYNC))
async_session_factory: async_sessionmaker = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)
