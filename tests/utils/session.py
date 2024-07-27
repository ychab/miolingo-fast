from asyncio import current_task

from sqlalchemy.ext.asyncio import async_scoped_session

from miolingo.db.session import async_session_factory

async_session_scoped: async_scoped_session = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=current_task,
)
