"""
Unit tests for RELINTs FastAPI endpoints using TestClient.
"""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from src.domain.entities import IncidentReport, Participant, BmGroup, RelintType
from src.adapters.sqlite_repo import SqliteRepo
from src.presentation.api.app import app
from src.presentation.api.dependencies import get_db_repo

@pytest.fixture
def mock_db_repo(tmp_path: Path):
    db_file = tmp_path / "test_api_relints.db"
    repo = SqliteRepo(db_file)
    
    # Insert sample test report
    report = IncidentReport(
        source_file="RELINT_001_TEST.pdf",
        subject="Homicídio qualificado em via pública",
        main_fact="Indivíduo alvejado por disparos de arma de fogo",
        date_of_fact="2026-08-10",
        time_of_fact="22:30",
        bm_group=BmGroup.OUTROS,
        relint_type=RelintType.OCORRENCIA,
        municipality="Porto Alegre",
        summary="Ataque a tiros resultante em um óbito.",
        content="CONTEÚDO INTEGRAL DO RELINT TESTE 001",
        participants=[
            Participant(name="João da Silva", nickname="Gordo", document="1234567890")
        ]
    )
    repo.save(report)
    return repo

@pytest.fixture
def client(mock_db_repo):
    # Override FastAPI dependency to use temporary test SQLite DB
    app.dependency_overrides[get_db_repo] = lambda: mock_db_repo
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_list_relints(client):
    response = client.get("/api/v1/relints")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["source_file"] == "RELINT_001_TEST.pdf"
    assert data[0]["subject"] == "Homicídio qualificado em via pública"
    assert data[0]["participants_count"] == 1

def test_get_relint_by_id(client):
    # First get the list to grab ID
    list_res = client.get("/api/v1/relints")
    relint_id = list_res.json()[0]["id"]

    detail_res = client.get(f"/api/v1/relints/{relint_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["source_file"] == "RELINT_001_TEST.pdf"
    assert detail["content"] == "CONTEÚDO INTEGRAL DO RELINT TESTE 001"
    assert len(detail["participants"]) == 1
    assert detail["participants"][0]["name"] == "João da Silva"

def test_update_relint(client):
    list_res = client.get("/api/v1/relints")
    relint_id = list_res.json()[0]["id"]

    update_payload = {
        "subject": "Homicídio Qualificado (Editado pelo usuário)",
        "summary": "Resumo atualizado manualmente."
    }
    put_res = client.put(f"/api/v1/relints/{relint_id}", json=update_payload)
    assert put_res.status_code == 200
    updated = put_res.json()
    assert updated["subject"] == "Homicídio Qualificado (Editado pelo usuário)"
    assert updated["summary"] == "Resumo atualizado manualmente."
    assert updated["user_edited"] is True
