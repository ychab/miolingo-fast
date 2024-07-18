from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from miolingo.db.base_class import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    first_name: Mapped[str] = mapped_column(String(length=512), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=512), nullable=False)

    @property
    def fullname(self) -> str:
        return f"{self.first_name} {self.last_name}"


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass
