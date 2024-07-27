from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from miolingo import settings

if settings.POSTGRES_URI is None:  # pragma: no cover
    raise RuntimeError("Did you forgot to export database env vars?")

async_engine: AsyncEngine = create_async_engine(url=str(settings.POSTGRES_URI))
async_session_factory: async_sessionmaker = async_sessionmaker(
    bind=async_engine,
    # Prevent attributes from being expired after commit/transaction.
    # @see https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.params.expire_on_commit
    expire_on_commit=False,
    autoflush=False,  # Require explicit .flush() in transaction to see changes
    autocommit=False,
)
