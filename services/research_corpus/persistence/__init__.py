from .interface import LiteratureRepository

__all__ = ["LiteratureRepository"]

from .interface import LiteratureRepository
from .repository import PostgreSQLLiteratureRepository

__all__ = [
    "LiteratureRepository",
    "PostgreSQLLiteratureRepository",
]