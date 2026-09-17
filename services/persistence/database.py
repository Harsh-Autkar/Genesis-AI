from collections.abc import Iterator
from contextlib import contextmanager
import os

import psycopg


DEFAULT_DATABASE_DSN = (
    "dbname=genesis_ai "
    "user=genesis "
    "password=genesis_local_dev_password "
    "host=localhost "
    "port=5433"
)


def get_database_dsn() -> str:
    """Return the configured PostgreSQL DSN."""
    return os.environ.get(
        "GENESIS_DATABASE_DSN",
        DEFAULT_DATABASE_DSN,
    )


def get_connection() -> psycopg.Connection:
    """Create a new PostgreSQL connection."""
    return psycopg.connect(get_database_dsn())


@contextmanager
def transaction() -> Iterator[psycopg.Connection]:
    """Provide a connection whose context commits or rolls back atomically."""
    with get_connection() as connection:
        yield connection