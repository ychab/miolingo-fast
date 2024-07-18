import logging.config
from typing import Any

LOGGER_MIOLINGO: str = "miolingo"

conf: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    # Default config for purpose, awaiting for override by settings just bellow.
    "loggers": {
        LOGGER_MIOLINGO: {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "alembic": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}


def configure_loggers(handlers: list[str], level: int, propagate: bool = False) -> None:
    """
    By careful, this function MUST be called AFTER any loggers have been already initialized.
    """
    # Change level only for our logger for now.
    conf["loggers"][LOGGER_MIOLINGO]["level"] = level

    # However, change handlers for all loggers defined to use the same.
    for logger in conf["loggers"].keys():
        conf["loggers"][logger]["handlers"] = handlers
        conf["loggers"][logger]["propagate"] = propagate

    # Then lets Python std lib do its jobs!
    logging.config.dictConfig(conf)
