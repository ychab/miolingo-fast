from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from miolingo import settings

if settings.POSTGRES_URI is None:  # pragma: no cover
    raise RuntimeError("Did you forgot to export database env vars?")

# Only used by factory_boy which didn't support natively async conn.
engine: Engine = create_engine(url=str(settings.POSTGRES_URI))
session_factory: sessionmaker = sessionmaker(bind=engine, autoflush=False, autocommit=False)
session_scoped: scoped_session = scoped_session(session_factory)
