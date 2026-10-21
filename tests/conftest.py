import os

import pytest

# Tests must never touch the development database. Default the environment
# before `up_vault.config` is imported; an explicit ENV from the shell wins.
os.environ.setdefault("ENV", "test")


@pytest.fixture(scope="session", autouse=True)
def require_test_database() -> None:
    """Fail fast when the configured database is not a test database."""
    from up_vault.database import engine

    database = engine.url.database
    if database is None or not database.endswith("_test"):
        pytest.fail(f"Tests must use a test database, got {database!r}.")
