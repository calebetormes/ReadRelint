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
registry_path = Path("data/processed_registry.json")

db_repo = SqliteRepo(db_path)
person_repo = SqlitePersonRepo(db_path)
processed_registry = JsonProcessedRegistry(registry_path)

# 1. Limpa tabelas para teste de re-extração
db_repo.clear_all()
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

# Procura a pasta de relints
input_dir = Path("relints_input")
if not input_dir.exists():
    input_dir = Path("data/relints")

if input_dir.exists():
    pdf_files = list(input_dir.glob("*.pdf"))
    print(f"Encontrados {len(pdf_files)} arquivos PDF na pasta {input_dir}")
    for pdf_file in pdf_files:
        print(f"Processando: {pdf_file.name}")
        etl_service.process_file(pdf_file)
else:
    print("Nenhuma pasta de PDFs encontrada em relints_input ou data/relints.")

print("\n--- TESTE DE VERIFICAÇÃO DE TABELAS ---")
import sqlite3
conn = sqlite3.connect('data/relints.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT COUNT(*) as count FROM relints")
print(f"Total RELINTs: {c.fetchone()['count']}")

c.execute("SELECT COUNT(*) as count FROM persons")
print(f"Total Pessoas em 'persons': {c.fetchone()['count']}")

c.execute("SELECT COUNT(*) as count FROM relint_participants")
print(f"Total Participações em 'relint_participants': {c.fetchone()['count']}")

c.execute("SELECT p.name, rp.participation_type, r.source_file FROM relint_participants rp JOIN persons p ON rp.person_id = p.id JOIN relints r ON rp.relint_id = r.id LIMIT 10")
rows = c.fetchall()
print("\nAmostra de Participantes inseridos:")
for row in rows:
    print(f"  - {row['name']} ({row['participation_type']}) no arquivo {row['source_file']}")

conn.close()
