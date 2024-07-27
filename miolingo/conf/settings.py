import logging
from pathlib import Path

from pydantic import (
    AnyHttpUrl,
    DirectoryPath,
    EmailStr,
    PostgresDsn,
    conint,
    field_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

from aiosmtplib.smtp import DEFAULT_TIMEOUT
from fastapi_mail import ConnectionConfig

PROJECT_DIR: Path = Path(__file__).parent.parent
BASE_DIR: Path = PROJECT_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MIOLINGO_",
        env_file=[BASE_DIR / ".env"],
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_DIR: Path = PROJECT_DIR

    DEBUG: bool = False

    LOG_LEVEL: int = logging.INFO
    LOG_HANDLERS: list[str] = ["default"]

    API_V1_STR: str = "/api/v1"

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    # DB connector
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_URI: MultiHostUrl | None = None

    # Mail connector
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_DEBUG: conint(gt=-1, lt=2) = 0  # type: ignore
    MAIL_FROM: EmailStr
    MAIL_FROM_NAME: str | None = None
    MAIL_TEMPLATE_FOLDER: DirectoryPath | None = PROJECT_DIR / "templates" / "mails"
    MAIL_SUPPRESS_SEND: conint(gt=-1, lt=2) = 0  # type: ignore
    MAIL_USE_CREDENTIALS: bool = True
    MAIL_VALIDATE_CERTS: bool = True
    MAIL_TIMEOUT: int = DEFAULT_TIMEOUT
    SMTP_CONFIG: ConnectionConfig | None = None

    # Frontend
    FRONTEND_URL_BASE: str
    FRONTEND_URL_RESET_PASSWORD: str
    FRONTEND_URL_VERIFY: str

    LANGUAGE_CODE: str = "fr-fr"

    SECRET: str

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def check_log_level(cls, v: int | str) -> int:
        if isinstance(v, int):
            return v

        level = logging.getLevelName(v)
        if isinstance(level, int):
            return level

        raise ValueError(v)

    @field_validator("POSTGRES_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> MultiHostUrl:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            host=info.data.get("POSTGRES_HOST"),
            port=info.data.get("POSTGRES_PORT"),
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            path=f"{info.data.get('POSTGRES_DB') or ''}",
        )

    @field_validator("SMTP_CONFIG", mode="before")
    @classmethod
    def assemble_smtp_connection(cls, v: str | None, info: ValidationInfo) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=info.data.get("MAIL_USERNAME"),
            MAIL_PASSWORD=info.data.get("MAIL_PASSWORD"),
            MAIL_PORT=info.data.get("MAIL_PORT"),
            MAIL_SERVER=info.data.get("MAIL_SERVER"),
            MAIL_STARTTLS=info.data.get("MAIL_STARTTLS"),
            MAIL_SSL_TLS=info.data.get("MAIL_SSL_TLS"),
            MAIL_DEBUG=info.data.get("MAIL_DEBUG"),
            MAIL_FROM=info.data.get("MAIL_FROM"),
            MAIL_FROM_NAME=info.data.get("MAIL_FROM_NAME"),
            TEMPLATE_FOLDER=info.data.get("MAIL_TEMPLATE_FOLDER"),
            SUPPRESS_SEND=info.data.get("MAIL_SUPPRESS_SEND"),
            USE_CREDENTIALS=info.data.get("MAIL_USE_CREDENTIALS"),
            VALIDATE_CERTS=info.data.get("MAIL_VALIDATE_CERTS"),
            TIMEOUT=info.data.get("MAIL_TIMEOUT"),
        )
