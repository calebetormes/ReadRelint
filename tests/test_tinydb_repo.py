import pytest
from pathlib import Path
from src.adapters.tinydb_repo import TinyDbRepo
from src.domain.entities import IncidentReport, Address, Participant, Vehicle

@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """
    Fixture que fornece um caminho de banco de dados temporário limpo para cada teste.
    """
    return tmp_path / "test_database.json"


def test_tinydb_repo_save_and_get_by_id(temp_db_path: Path):
    repo = TinyDbRepo(temp_db_path)
    
    report = IncidentReport(
        incident_group="Ocorrências do AVANTE",
        incident_type="Furto de Veículo",
        address=Address(street="Rua Alegre", number="123", neighborhood="Bairro Feliz", city="Sorocaba"),
        participants=[
            Participant(name="Alice", role="Comunicante"),
            Participant(name="Bob", role="Vítima")
        ],
        vehicles=[
            Vehicle(plate="AAA-9999", model="Bicicleta Caloi", color="Preta")
        ],
        attending_officer="Cabo Oliveira",
        history_summary="Subtração de bicicleta que estava presa em poste público."
    )
    
    # Salva e verifica se retorna um ID tipo string
    report_id = repo.save(report)
    assert isinstance(report_id, str)
    assert report_id.isdigit()
    
    # Recupera o registro do banco
    saved_report = repo.get_by_id(report_id)
    assert saved_report is not None
    assert saved_report.incident_group == "Ocorrências do AVANTE"
    assert saved_report.incident_type == "Furto de Veículo"
    assert saved_report.address.street == "Rua Alegre"
    assert len(saved_report.participants) == 2
    assert saved_report.participants[0].name == "Alice"
    assert saved_report.participants[1].role == "Vítima"
    assert len(saved_report.vehicles) == 1
    assert saved_report.vehicles[0].plate == "AAA-9999"
    assert saved_report.attending_officer == "Cabo Oliveira"
    assert saved_report.history_summary == "Subtração de bicicleta que estava presa em poste público."

    # Verifica se os caracteres especiais foram salvos sem escape unicode no arquivo JSON
    file_content = temp_db_path.read_text(encoding="utf-8")
    assert "Vítima" in file_content
    assert "Subtração" in file_content
    assert "\\u00ed" not in file_content


def test_tinydb_repo_get_by_invalid_or_nonexistent_id(temp_db_path: Path):
    repo = TinyDbRepo(temp_db_path)
    
    # ID não numérico
    assert repo.get_by_id("id-invalido") is None
    
    # ID numérico mas que não existe no banco
    assert repo.get_by_id("9999") is None


def test_tinydb_repo_get_all(temp_db_path: Path):
    repo = TinyDbRepo(temp_db_path)
    
    # Inicialmente vazio
    assert repo.get_all() == []
    
    report1 = IncidentReport(
        incident_group="Ocorrências do AVANTE",
        incident_type="Roubo de Veículo",
        address=Address(street="Av Central"),
        history_summary="Roubo simples."
    )
    
    report2 = IncidentReport(
        incident_group="Demais Fatos",
        incident_type="Estelionato",
        address=Address(street="Internet"),
        history_summary="Golpe do Pix."
    )
    
    # Salva dois registros
    repo.save(report1)
    repo.save(report2)
    
    all_reports = repo.get_all()
    assert len(all_reports) == 2
    
    types = [r.incident_type for r in all_reports]
    assert "Roubo de Veículo" in types
    assert "Estelionato" in types


def test_tinydb_repo_exists_by_source_file(temp_db_path: Path):
    repo = TinyDbRepo(temp_db_path)
    
    # Verifica que não existe antes de inserir
    assert not repo.exists_by_source_file("bo_123.pdf")
    
    report = IncidentReport(
        incident_group="Ocorrências do AVANTE",
        incident_type="Roubo de Veículo",
        address=Address(street="Av Central"),
        history_summary="Roubo simples.",
        source_file="bo_123.pdf"
    )
    
    repo.save(report)
    
    # Verifica que agora existe
    assert repo.exists_by_source_file("bo_123.pdf")
    # Arquivo com outro nome não deve constar
    assert not repo.exists_by_source_file("bo_456.pdf")

