import pytest
from pathlib import Path
from src.domain.entities import IncidentReport, Person, Municipality
from src.adapters.sqlite_repo import SqliteRepo
from src.adapters.sqlite_person_repo import SqlitePersonRepo
from src.adapters.sqlite_municipality_repo import SqliteMunicipalityRepo


def test_sqlite_repo_crud(tmp_path: Path):
    db_file = tmp_path / "test_relints.db"
    repo = SqliteRepo(db_file)

    report = IncidentReport(
        source_file="relint_test_01.pdf",
        subject="PRISÃO POR ROUBO",
        summary="Ocorrência de roubo em Panambi",
        content="Conteúdo completo do histórico."
    )

    # 1. Save
    doc_id = repo.save(report)
    assert doc_id != ""

    # 2. Exists & Get
    assert repo.exists_by_source_file("relint_test_01.pdf") is True
    assert repo.exists_by_source_file("inexistente.pdf") is False

    fetched = repo.get_by_id(doc_id)
    assert fetched is not None
    assert fetched.subject == "PRISÃO POR ROUBO"
    assert fetched.source_file == "relint_test_01.pdf"

    by_file = repo.get_by_source_file("relint_test_01.pdf")
    assert by_file is not None
    assert by_file.summary == "Ocorrência de roubo em Panambi"

    # 3. Get All
    all_reports = repo.get_all()
    assert len(all_reports) == 1

    # 4. Upsert (Save same source_file with updated content)
    report_updated = IncidentReport(
        source_file="relint_test_01.pdf",
        subject="PRISÃO POR ROUBO ATUALIZADO",
        summary="Resumo atualizado",
        content="Novo conteúdo."
    )
    repo.save(report_updated)
    all_reports_after = repo.get_all()
    assert len(all_reports_after) == 1
    assert all_reports_after[0].subject == "PRISÃO POR ROUBO ATUALIZADO"

    # 5. Delete
    deleted = repo.delete_by_source_file("relint_test_01.pdf")
    assert deleted is True
    assert repo.exists_by_source_file("relint_test_01.pdf") is False
    assert len(repo.get_all()) == 0


def test_sqlite_person_repo_crud(tmp_path: Path):
    db_file = tmp_path / "test_persons.db"
    person_repo = SqlitePersonRepo(db_file)

    person = Person(
        person_id="123456789",
        name="Carlos da Silva",
        aliases=["Carlinhos"],
        documents=["123.456.789-00"],
        linked_relints=["relint_01.pdf"]
    )

    # Save
    pid = person_repo.save(person)
    assert pid == "123456789"

    # Get by ID
    fetched = person_repo.get_by_id("123456789")
    assert fetched is not None
    assert fetched.name == "Carlos da Silva"
    assert "Carlinhos" in fetched.aliases

    # Get by Document
    by_doc = person_repo.get_by_document("12345678900")
    assert by_doc is not None
    assert by_doc.person_id == "123456789"

    # Update
    person.aliases.append("Novo Apelido")
    person_repo.update(person)
    updated = person_repo.get_by_id("123456789")
    assert updated is not None
    assert "Novo Apelido" in updated.aliases

    # Get All
    assert len(person_repo.get_all()) == 1


def test_sqlite_municipality_repo_crud(tmp_path: Path):
    db_file = tmp_path / "test_muns.db"
    mun_repo = SqliteMunicipalityRepo(db_file)

    mun = Municipality(
        name="Panambi",
        linked_relints=["relint_01.pdf"],
        stats_by_group={"Roubo": 2}
    )

    # Save
    name = mun_repo.save(mun)
    assert name == "Panambi"

    # Get by Name (Case Insensitive)
    fetched = mun_repo.get_by_name("panambi")
    assert fetched is not None
    assert fetched.name == "Panambi"
    assert fetched.stats_by_group.get("Roubo") == 2

    # Update
    mun.stats_by_group["Furtos"] = 1
    mun_repo.update(mun)
    updated = mun_repo.get_by_name("PANAMBI")
    assert updated is not None
    assert updated.stats_by_group.get("Furtos") == 1

    # Clear All
    mun_repo.clear_all()
    assert len(mun_repo.get_all()) == 0

