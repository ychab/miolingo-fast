from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """
    @see https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-orm
    """

    pass


class BaseModelMixin:
    """
    https://docs.sqlalchemy.org/en/20/orm/declarative_mixins.html
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"miolingo_{cls.__name__.lower()}"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
