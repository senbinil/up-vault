"""Domain and persistence models.

Importing this package registers every model on ``Base.metadata`` so that
``alembic revision --autogenerate`` can discover it. Add each new model module
to the imports below as it is introduced, or autogenerate will silently emit an
empty migration.
"""

from up_vault.models.base import Base

__all__ = ["Base"]
