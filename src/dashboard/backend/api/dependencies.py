"""
Dependency providers for FastAPI controllers.
"""
from pathlib import Path
import os
from src.dashboard.backend.database.sqlite_repo import SqliteRepo
from src.dashboard.backend.database.sqlite_person_repo import SqlitePersonRepo

# Default database path
DEFAULT_DB_PATH = Path(os.getenv("RELINT_DB_PATH", "data/relints.db"))

_main_controller_instance = None

def set_main_controller(controller):
    global _main_controller_instance
    _main_controller_instance = controller

def get_main_controller():
    global _main_controller_instance
    if _main_controller_instance is None:
        from src.dashboard.desktop.controllers.main_controller import MainController
        _main_controller_instance = MainController()
    return _main_controller_instance

def get_db_repo() -> SqliteRepo:
    """Returns initialized SqliteRepo instance."""
    return SqliteRepo(DEFAULT_DB_PATH)

def get_person_repo() -> SqlitePersonRepo:
    """Returns initialized SqlitePersonRepo instance."""
    return SqlitePersonRepo(DEFAULT_DB_PATH)
