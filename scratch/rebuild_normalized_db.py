import os
import sys
from pathlib import Path
sys.path.insert(0, '.')

from src.adapters.sqlite_repo import SqliteRepo
from src.adapters.sqlite_person_repo import SqlitePersonRepo
from src.adapters.json_processed_registry import JsonProcessedRegistry
from src.application.etl_service import EtlService
from src.adapters.pdf_reader import PdfReader
from src.adapters.ollama_client import OllamaClient

db_path = Path("data/relints.db")
registry_path = Path("data/processed_history.json")

db_repo = SqliteRepo(db_path)
db_repo.clear_all()
person_repo = SqlitePersonRepo(db_path)
processed_registry = JsonProcessedRegistry(registry_path)
processed_registry.clear()
pdf_reader = PdfReader()
llm_client = OllamaClient()

etl_service = EtlService(
    file_parser=pdf_reader,
    llm_processor=llm_client,
    database_repo=db_repo,
    processed_registry=processed_registry,
    person_repo=person_repo
)

input_dir = Path("relints_input")
if input_dir.exists():
    for pdf_file in input_dir.glob("*.pdf"):
        print(f"Processando e inserindo no modelo relacional: {pdf_file.name}")
        etl_service.process_file(pdf_file)

print("Novo banco de dados 100% relacional normalizado criado com sucesso!")
