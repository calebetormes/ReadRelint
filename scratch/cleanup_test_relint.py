import sys
from pathlib import Path
sys.path.insert(0, '.')

from src.adapters.sqlite_repo import SqliteRepo

repo = SqliteRepo(Path("data/relints.db"))
repo.delete_by_source_file("RELINT_TESTE_PARTICIPANTES.pdf")
print("RELINT de teste removido da base de dados local.")
