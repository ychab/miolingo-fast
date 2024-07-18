from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, declarative_base, declared_attr, mapped_column

Base = declarative_base()


class BaseModelMixin:
    """
    https://docs.sqlalchemy.org/en/20/orm/declarative_mixins.html
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"miolingo_{cls.__name__.lower()}"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
