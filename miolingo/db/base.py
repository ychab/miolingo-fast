# Import all the models, so that Base has them before being imported by Alembic
from miolingo.db.base_class import Base  # noqa
from miolingo.models import *  # noqa
