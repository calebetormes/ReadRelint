import sys
from pathlib import Path
sys.path.insert(0, '.')

from src.adapters.sqlite_repo import SqliteRepo
from src.adapters.sqlite_person_repo import SqlitePersonRepo
from src.adapters.json_processed_registry import JsonProcessedRegistry
from src.application.etl_service import EtlService
from src.adapters.pdf_reader import PdfReader
from src.adapters.ollama_client import OllamaClient
from src.domain.rules.relint_rule import RelintRule

db_path = Path("data/relints.db")
registry_path = Path("data/processed_registry.json")

db_repo = SqliteRepo(db_path)
person_repo = SqlitePersonRepo(db_path)
processed_registry = JsonProcessedRegistry(registry_path)

# Limpa o banco e o histórico para re-extração limpa
print("Limpando banco e registro de histórico...")
db_repo.clear_all()
person_repo.clear_all()
processed_registry.clear()

pdf_reader = PdfReader()
llm_client = OllamaClient()
relint_rule = RelintRule()

etl_service = EtlService(
    file_parser=pdf_reader,
    llm_processor=llm_client,
    database_repo=db_repo,
    processed_registry=processed_registry,
    person_repo=person_repo
)

testez_dir = Path(r"C:\Users\admin\Desktop\testez")
if testez_dir.exists():
    pdf_files = list(testez_dir.glob("*.pdf"))
    print(f"Encontrados {len(pdf_files)} arquivos PDF na pasta {testez_dir}:")
    for pdf_file in pdf_files:
        print(f" -> Processando: {pdf_file.name}")
        etl_service.process_file(pdf_file, rule=relint_rule)
else:
    print(f"Pasta {testez_dir} não encontrada.")

print("\n================ VERIFICAÇÃO DO BANCO ================")
import sqlite3
conn = sqlite3.connect('data/relints.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT COUNT(*) as cnt FROM relints")
print(f"Total na tabela 'relints': {c.fetchone()['cnt']}")

c.execute("SELECT COUNT(*) as cnt FROM persons")
print(f"Total na tabela 'persons': {c.fetchone()['cnt']}")

c.execute("SELECT COUNT(*) as cnt FROM relint_participants")
print(f"Total na tabela 'relint_participants': {c.fetchone()['cnt']}")

print("\n--- AMOSTRA DE PESSOAS CADASTRADAS ('persons') ---")
c.execute("SELECT id, person_key, name, nickname, document FROM persons LIMIT 10")
for pr in c.fetchall():
    print(f" - ID {pr['id']} | Nome: {pr['name']} | Vulgo: {pr['nickname']} | Doc: {pr['document']}")

print("\n--- AMOSTRA DE PARTICIPAÇÕES ('relint_participants') ---")
c.execute("""
    SELECT rp.id, p.name, rp.participation_type, r.source_file
    FROM relint_participants rp
    JOIN persons p ON rp.person_id = p.id
    JOIN relints r ON rp.relint_id = r.id
    LIMIT 15
""")
for pt in c.fetchall():
    print(f" - {pt['name']} ({pt['participation_type']}) -> {pt['source_file']}")

conn.close()
