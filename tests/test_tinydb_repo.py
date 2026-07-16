import pytest
from pathlib import Path
from src.adapters.tinydb_repo import TinyDbRepo
from src.domain.entities import IncidentReport

@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """
    Fixture que fornece um caminho de banco de dados temporário limpo para cada teste.
    """
    return tmp_path / "test_database.json"

def test_tinydb_repo_save_and_get_by_id(temp_db_path: Path):
    repo = TinyDbRepo(temp_db_path)
    
    report = IncidentReport(
        source_file="bo_123.pdf",
        content="Subtração de bicicleta que estava presa em poste público com acentuação."
    )
    
    # Salva e verifica se retorna um ID tipo string
    report_id = repo.save(report)
    assert isinstance(report_id, str)
    assert report_id.isdigit()
    
    # Recupera o registro do banco
    saved_report = repo.get_by_id(report_id)
    assert saved_report is not None
    assert saved_report.source_file == "bo_123.pdf"
    assert saved_report.content == "Subtração de bicicleta que estava presa em poste público com acentuação."

    # Verifica se os caracteres especiais foram salvos sem escape unicode no arquivo JSON
    file_content = temp_db_path.read_text(encoding="utf-8")
    assert "Subtração" in file_content
    assert "\\u00e7" not in file_content

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
        source_file="doc1.pdf",
        content="Conteúdo um"
    )
    
    report2 = IncidentReport(
        source_file="doc2.pdf",
        content="Conteúdo dois"
    )
    
    # Salva dois registros
    repo.save(report1)
    repo.save(report2)
    
    all_reports = repo.get_all()
    assert len(all_reports) == 2
    
    sources = [r.source_file for r in all_reports]
    assert "doc1.pdf" in sources
    assert "doc2.pdf" in sources

def test_tinydb_repo_exists_by_source_file(temp_db_path: Path):
    repo = TinyDbRepo(temp_db_path)
    
    # Verifica que não existe antes de inserir
    assert not repo.exists_by_source_file("bo_123.pdf")
    
    report = IncidentReport(
        source_file="bo_123.pdf",
        content="Conteúdo simples."
    )
    
    repo.save(report)
    
    # Verifica que agora existe
    assert repo.exists_by_source_file("bo_123.pdf")
    # Arquivo com outro nome não deve constar
    assert not repo.exists_by_source_file("bo_456.pdf")
