"""
Dependency providers for FastAPI controllers.
"""
from pathlib import Path
import os
from src.adapters.sqlite_repo import SqliteRepo
from src.adapters.sqlite_person_repo import SqlitePersonRepo

# Default database path
DEFAULT_DB_PATH = Path(os.getenv("RELINT_DB_PATH", "data/relints.db"))

def get_db_repo() -> SqliteRepo:
    """Returns initialized SqliteRepo instance."""
    return SqliteRepo(DEFAULT_DB_PATH)

def get_person_repo() -> SqlitePersonRepo:
    """Returns initialized SqlitePersonRepo instance."""
    return SqlitePersonRepo(DEFAULT_DB_PATH)
