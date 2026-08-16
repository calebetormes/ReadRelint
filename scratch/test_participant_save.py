import sys
from pathlib import Path
sys.path.insert(0, '.')

from src.adapters.sqlite_repo import SqliteRepo
from src.domain.entities import IncidentReport, Participant

db_file = Path("scratch/test_part.db")
if db_file.exists():
    db_file.unlink()

repo = SqliteRepo(db_file)

p1 = Participant(name="João Teste", nickname="Jotinha", document="12345678900", participation_type="Acusado")
p2 = {"name": "Maria Teste", "nickname": "Mary", "document": "98765432100", "participation_type": "Vítima"}

report = IncidentReport(
    source_file="test_doc.pdf",
    subject="Teste Participantes",
    participants=[p1, p2]
)

doc_id = repo.save(report)
print(f"Salvo com doc_id: {doc_id}")

fetched = repo.get_by_id(doc_id)
print(f"Participantes recuperados: {len(fetched.participants)}")
for p in fetched.participants:
    print(f"- {p.name} ({p.participation_type}) | Nick: {p.nickname} | Doc: {p.document}")
