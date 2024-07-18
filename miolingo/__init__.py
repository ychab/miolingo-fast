import logging

from miolingo.conf.loggers import LOGGER_MIOLINGO  # noqa
from miolingo.conf.settings import Settings

VERSION = (0, 0, 1)
__version__ = ".".join(map(str, VERSION))

# Load settings at root package level to be available as quickly as possible.
settings = Settings()

# Declare logger here to be available at root package, but would be configured later.
logger: logging.Logger = logging.getLogger(LOGGER_MIOLINGO)
