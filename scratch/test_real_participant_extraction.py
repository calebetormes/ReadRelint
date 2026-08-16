import sys
from pathlib import Path
sys.path.insert(0, '.')

from src.adapters.sqlite_repo import SqliteRepo
from src.adapters.sqlite_person_repo import SqlitePersonRepo
from src.domain.entities import IncidentReport, Participant

db_path = Path("data/relints.db")
db_repo = SqliteRepo(db_path)
person_repo = SqlitePersonRepo(db_path)

# Criando um RELINT de teste com 2 participantes para validar a gravação relacional
p1 = Participant(
    name="MARCOS ANTONIO DOS SANTOS",
    nickname="MARQUINHOS",
    document="012.345.678-99",
    background="Tráfico de drogas",
    participation_type="Acusado"
)

p2 = Participant(
    name="ROBERTO SILVA OLIVEIRA",
    nickname="BETO",
    document="987.654.321-00",
    background="Sem antecedentes",
    participation_type="Vítima"
)

report = IncidentReport(
    source_file="RELINT_TESTE_PARTICIPANTES.pdf",
    subject="OCORRÊNCIA DE TESTE COM PARTICIPANTES",
    main_fact="Tentativa de homicídio",
    bm_group="Homicídio",
    relint_type="Ocorrência",
    municipality="Panambi",
    police_unit="39º BPM",
    summary="Resumo de teste de participantes.",
    content="HISTÓRICO INTEGRAL DE TESTE.",
    participants=[p1, p2]
)

relint_id = db_repo.save(report)
print(f"RELINT salvo com ID: {relint_id}")

import sqlite3
conn = sqlite3.connect('data/relints.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT id, source_file, subject, police_unit FROM relints WHERE source_file = 'RELINT_TESTE_PARTICIPANTES.pdf'")
relint_row = c.fetchone()
print(f"\n1. Tabela 'relints': {dict(relint_row)}")

c.execute("SELECT * FROM persons")
person_rows = c.fetchall()
print(f"\n2. Tabela 'persons' ({len(person_rows)} registros):")
for pr in person_rows:
    print(f"   - ID: {pr['id']} | Key: {pr['person_key']} | Nome: {pr['name']} | Vulgo: {pr['nickname']} | Doc: {pr['document']}")

c.execute("""
    SELECT rp.id as relint_part_id, r.source_file, p.name, rp.participation_type
    FROM relint_participants rp
    JOIN persons p ON rp.person_id = p.id
    JOIN relints r ON rp.relint_id = r.id
""")
part_rows = c.fetchall()
print(f"\n3. Tabela 'relint_participants' ({len(part_rows)} registros):")
for pt in part_rows:
    print(f"   - Linha {pt['relint_part_id']}: {pt['name']} ({pt['participation_type']}) em {pt['source_file']}")

conn.close()
